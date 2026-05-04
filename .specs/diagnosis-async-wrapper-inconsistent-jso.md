# Fix async_wrapper inconsistent JSON output

## Symptom

The `_run_module` function in `async_wrapper.py` produces inconsistent JSON output across exit paths:

1. **Normal completion** — Writes `result` dict with module's JSON to `tmp_job_path`, renames to `job_path`. Uses `json.dumps(result)`.
2. **OSError/IOError** — Writes `{"failed": 1, "cmd": ..., "msg": ..., "outdata": ..., "stderr": ..., "ansible_job_id": ...}` to `tmp_job_path`, renames to `job_path`.
3. **ValueError/Exception** — Writes `{"failed": 1, "cmd": ..., "data": ..., "stderr": ..., "msg": ..., "ansible_job_id": ...}` to `tmp_job_path`, renames to `job_path`.

Inconsistent field names:
- `"failed": 1` (integer) in error paths vs. no explicit `failed` field in normal path (relies on module's own `failed` key).
- `"outdata"` in OSError path vs. `"data"` in ValueError path (both storing the same stdout content).
- Error result dicts are unordered and mix conventions.

Also, the initial job status write at lines 132-135 writes `{"started": 1, "finished": 0, "ansible_job_id": jid}` — the `finished` field is an integer while it should ideally be consistent.

The test `test_run_module` expects:
- `jres.get('rc') == 0` — the module's own JSON output is parsed from the job file.
- `jres.get('stderr') == 'stderr stuff'` — stderr should be present in the result.

## Root cause

The `_run_module` function (lines 129-202) has three try/except blocks that each construct result dictionaries with different field names for the same concepts. Specifically:

- Line 180-186 (OSError/IOError): uses `"outdata"` field name
- Line 190-198 (ValueError/Exception): uses `"data"` field name

These should both use `"outdata"` consistently. Additionally, error paths don't include `"stderr"` in a consistent manner — the OSError path properly includes it, but the field naming mismatch with `"data"` vs `"outdata"` causes confusion.

## Candidate fix

1. In the ValueError/Exception handler (line 190-198), change `"data"` to `"outdata"` to match the naming convention used in the OSError handler.

This is the minimal change needed to pass the existing tests and improve consistency. The test checks that the job file contains a parsed JSON with correct `rc` and `stderr` — fixing the `"data"` → `"outdata"` discrepancy ensures that in all code paths, module stdout is stored under `outdata`, and the module's own result fields (`rc`, `stderr`) are preserved correctly.

## Verification

After the fix, run:
```
pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v
```
