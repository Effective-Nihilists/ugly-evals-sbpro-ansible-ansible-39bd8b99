# Diagnosis: async_wrapper inconsistent JSON output

## Symptoms

The `_run_module` function in `lib/ansible/modules/async_wrapper.py` produces inconsistent JSON output across its three exit paths (success, OSError/IOError, ValueError/Exception). Three concrete inconsistencies:

1. **`ansible_job_id` missing from success path** — The success path (lines 162-176) writes `result = json.loads(filtered_outdata)` then optionally adds `stderr`, but never adds `ansible_job_id`. Both error paths explicitly set `result['ansible_job_id'] = jid`.

2. **`failed` field type mismatch** — Error paths inside `_run_module` use integer `"failed": 1` (lines 181, 192). The `main()` function uses boolean `"failed": True` (lines 208, 337). This type inconsistency breaks automated consumers.

3. **Inconsistent field naming in error dicts** — The OSError/IOError handler uses key `"outdata"` (line 184) while the ValueError handler uses key `"data"` (line 195) for the same purpose (captured stdout).

## Root cause

The `_run_module` function grew error-handling blocks that were written independently without a shared output template. Each `except` branch constructs its own result dictionary from scratch rather than building from a common base, and the success path doesn't normalize the result at all (it passes through the module's raw JSON verbatim).

## Candidate fixes

### Fix A (minimal): Add `ansible_job_id` and standardize `failed` type
- After `result = json.loads(filtered_outdata)` on success, add `result['ansible_job_id'] = jid`
- Change `"failed": 1` to `"failed": True` in both error handlers
- Unify `outdata`/`data` to a single field name (e.g., `outdata`)
- **Tradeoff**: Small diff, single function modified. The output is still shaped differently between success (module params) and errors (wrapper params), but all paths include `ansible_job_id` and use boolean `failed`.

### Fix B (consistent): Use `ansible_job_id` in success path only
- Add `result['ansible_job_id'] = jid` in the success path
- Keep error paths as-is since they already have `ansible_job_id`
- **Tradeoff**: Smaller diff, but `failed` type mismatch remains.

### Chosen fix: Fix A (minimal) — standardize types AND add job_id in success path
- Adds `ansible_job_id` to the success path result
- Changes `"failed": 1` → `"failed": True` in both error handlers for type consistency with `main()`
- Unifies `"data"` → `"outdata"` in ValueError handler for field-name consistency with OSError handler
- Single file, ~4 line changes, no behavioral regression risk
