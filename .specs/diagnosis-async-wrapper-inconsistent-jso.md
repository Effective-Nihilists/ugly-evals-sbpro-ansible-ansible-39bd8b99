# Diagnosis: async_wrapper Inconsistent JSON Output

## Symptom
Test `test_run_module` may be flaky or failing. The ticket describes inconsistent JSON output across exit paths in `async_wrapper.py` — specifically missing `ansible_job_id` on some error paths, inconsistent field names (`msg` vs `data` for stdout), and non-standardized error messages.

## Root Cause Analysis

Examined `lib/ansible/modules/async_wrapper.py`. The code has **known structural inconsistencies** across its three exit paths in `_run_module` (lines 129–202):

### Issue 1: OSError vs ValueError handler field inconsistency
- **OSError handler (line 178–188)**: uses `"outdata"` for stdout content
- **ValueError handler (line 190–199)**: uses `"data"` for stdout content

This means callers processing the job file get different field names depending on which exception occurred. The test expects consistent `stderr` fields but also expects `rc` from the module output — the ValueError handler would not include `rc`.

### Issue 2: `ansible_job_id` ordering
Both exception handlers add `result['ansible_job_id'] = jid` **after** building the result dict, then write. This is correct but verbose — the field is added only in error paths, not in the normal path (where it comes from module output). The `main()` error handler at line 336 does NOT include `ansible_job_id`, only `failed` and `msg`.

### Issue 3: `_filter_non_json_lines` can raise `ValueError`
If module output doesn't parse as valid JSON (e.g., the filter strips too much), a `ValueError` is raised. The ValueError handler returns:
```python
result = {
    "failed": 1,
    "cmd": wrapped_cmd,
    "data": outdata,
    "stderr": stderr,
    "msg": traceback.format_exc()
}
```
This result does NOT have `rc`, `ansible_job_id`, or consistent field names — test assertions would fail.

## Candidate Fixes

### Option A: Normalize field names in exception handlers (safe, minimal)
- Change `"data"` to `"outdata"` in the ValueError handler to match the OSError handler
- Add `"rc": 1` or similar to error results so callers can distinguish success from failure
- Add `ansible_job_id` to the `main()` error handler

### Option B: Add try/finally for jobfile cleanup (robust)
- Ensure jobfile is always closed and renamed even if exceptions propagate
- Currently `jobfile.close()` and `os.rename()` could be skipped if an exception escapes

### Option C: Add try/except around `_filter_non_json_lines` (defensive)
- Wrap the filter call to handle ValueError gracefully, preserving `stderr`

## Recommendation
Apply **Option A** (normalize field names + add `ansible_job_id` to `main()` error handler). This addresses the documented inconsistency without changing test expectations. Also add `rc: 1` to error results so the test's `jres.get('rc') == 0` only passes on actual success.

## Files to Modify
- `lib/ansible/modules/async_wrapper.py` — lines 178–199 (exception handlers), line 336 (main error handler)