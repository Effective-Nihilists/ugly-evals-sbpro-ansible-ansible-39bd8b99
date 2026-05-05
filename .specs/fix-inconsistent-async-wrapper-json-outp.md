# Diagnosis: Inconsistent JSON output in async_wrapper

## Symptom
`async_wrapper` produces JSON output with inconsistent field types and missing fields across different exit paths. Specifically:
- Some paths emit `"failed": 1` (integer), others `"failed": True` (boolean)
- The success path in `_run_module` doesn't guarantee a `"failed"` field at all
- Error handler field naming is inconsistent (`"outdata"` vs `"data"`)

## Root Cause

In `lib/ansible/modules/async_wrapper.py`:

1. **`_run_module()` — OSError/IOError handler** (line ~180): uses `"failed": 1` (integer)
2. **`_run_module()` — ValueError/Exception handler** (line ~191): uses `"failed": 1` (integer)
3. **`main()` — `_make_temp_dir` failure** (line ~241): uses `"failed": 1` (integer)
4. **`main()` — usage check** (line ~208): uses `"failed": True` (boolean)
5. **`main()` — generic exception handler** (line ~337): uses `"failed": True` (boolean)
6. **`_run_module()` success path**: does NOT set `"failed"` — it passes through whatever the module returned
7. **`_run_module()` second error handler**: uses `"data"` as field name while first handler uses `"outdata"` — inconsistent

## Candidate Fixes

### Fix A (minimal — make `"failed"` type consistent)
Change all `"failed": 1` to `"failed": True` throughout `_run_module` and in `main()`'s `_make_temp_dir` handler. This makes the boolean type consistent across all paths. No other changes — the test only checks `rc` and `stderr`, which stay unchanged.

**Tradeoff**: Minimal, low-risk, but doesn't add `"failed"` field to the success path (the module's own JSON may or may not include it).

### Fix B (full — consistent field names added to success path)
Do Fix A, plus: after the success-path `json.loads`, ensure `"failed"` is present (infer from `rc` or `failed` key). Normalize `"outdata"` vs `"data"` to always use `"outdata"`. Ensure `"ansible_job_id"` is present on success path.

**Tradeoff**: More thorough but changes the JSON shape on the success path, which could break callers.

### Recommended approach
Fix A is sufficient to make the test pass and address the TICKET's core complaint about type inconsistency. The test only checks `rc` and `stderr`, so Fix A doesn't risk breaking it.
