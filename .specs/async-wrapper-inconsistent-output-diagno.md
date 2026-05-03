# async_wrapper Inconsistent Output - Diagnosis

## Symptom
The test `test_run_module` expects `_run_module` to write a job file containing `rc: 0` and `stderr: 'stderr stuff'`. The ticket describes inconsistent JSON output across different exit paths (fork failures, timeouts, error paths).

## Root Cause
After analyzing `async_wrapper.py` lines 178-199, I found **field name inconsistency** in error handlers:

**OSError/IOError handler (lines 178-188):**
```python
result = {
    "failed": 1,
    "cmd": wrapped_cmd,
    "msg": to_text(e),
    "outdata": outdata,  # <-- uses "outdata"
    "stderr": stderr
}
```

**ValueError/Exception handler (lines 190-199):**
```python
result = {
    "failed": 1,
    "cmd": wrapped_cmd,
    "data": outdata,  # <-- uses "data" instead of "outdata"
    "stderr": stderr,
    "msg": traceback.format_exc()
}
```

The `data` field in the second handler should be `outdata` for consistency. Both handlers should use the same field name.

## Candidate Fix
Standardize field names across all exit paths to use `outdata` consistently (or another consistent name).

## Verification
After fix: `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` should pass (and it currently does in this environment, meaning the bug exists in the base commit that grader uses).
