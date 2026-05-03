# async_wrapper Inconsistent Output — Diagnosis

## Symptom
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` expects `jres.get('rc') == 0` and `jres.get('stderr') == 'stderr stuff'`. The code must produce a consistent JSON object for the job result file across all exit paths, including success, fork errors, and timeout paths. The ticket describes inconsistent field names (`data` vs `outdata`, `msg` fields), missing `ansible_job_id` in the success path, and non-standardized error messages.

## Root Cause

### Bug 1: `ansible_job_id` missing in success path
In `_run_module` (lines 176-199), `ansible_job_id` is added to the result dict only in the exception handlers (lines 187, 198):
```python
result['ansible_job_id'] = jid  # only in exception paths
```
In the success path (lines 162-176), `ansible_job_id` is never added to the result before writing it to the job file.

### Bug 2: Inconsistent field names in exception handlers
The OSError handler (lines 178-188) uses `outdata` as the field name:
```python
result = {
    "failed": 1,
    "cmd": wrapped_cmd,
    "msg": to_text(e),
    "outdata": outdata,  # temporary notice only
    "stderr": stderr
}
```
But the ValueError/Exception handler (lines 190-199) uses `data`:
```python
result = {
    "failed": 1,
    "cmd": wrapped_cmd,
    "data": outdata,  # temporary notice only
    "stderr": stderr,
    "msg": traceback.format_exc()
}
```
This inconsistency means callers get `outdata` in some failure cases and `data` in others.

## Candidate Fixes

1. **Add `ansible_job_id` to success path** (before line 176): Add `result['ansible_job_id'] = jid` before `jobfile.write(json.dumps(result))`.

2. **Standardize exception handler field names**: Change `data` to `outdata` in the ValueError/Exception handler (line 194) to match the OSError handler. Keep `msg` field consistent across both handlers.

3. **Run test** to verify fixes.

These are surgical changes that fix the documented inconsistencies without altering the logic of the module execution.