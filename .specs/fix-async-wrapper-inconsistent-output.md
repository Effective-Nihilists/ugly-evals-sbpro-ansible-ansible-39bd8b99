# Fix async_wrapper inconsistent output

## Diagnosis

**Root cause**: In `_run_module()` at `lib/ansible/modules/async_wrapper.py:178-188`, the `OSError/IOError` exception handler writes a JSON result to the job file without a `rc` field. The test writes a job file with `rc: 0`, calls `_run_module()` which triggers an OSError (e.g., `/usr/bin/python` doesn't exist in the Docker test environment), and the job file result has no `rc` key → `jres.get('rc')` returns `None` → test fails.

**Also inconsistent**: The `ValueError/Exception` handler uses `"data"` for output while the OSError handler uses `"outdata"` — non-uniform field names across error paths.

## Fix

1. Add `rc` field to the OSError handler result (line ~187), sourced from `result.get('rc')` — consistent with how `rc` comes from module JSON in the normal path.
2. Add `rc` field to the ValueError handler result for consistency.
3. Standardize `stderr` inclusion in OSError handler.

## Files

- `lib/ansible/modules/async_wrapper.py` — `_run_module()` function, two exception handlers