# Diagnosis: async_wrapper inconsistent JSON output

## Symptom
The `async_wrapper` module produces inconsistent information across exit paths:
1. Fork #2 failure outputs plain text instead of JSON
2. Async directory creation failure uses `"failed": 1` (integer) instead of `"failed": True` (boolean)
3. Timeout exits with `sys.exit(0)` - no JSON output, missing child PID context

## Root Cause
Three code paths in `lib/ansible/modules/async_wrapper.py` don't produce consistent JSON output:

1. **Line 67** (fork #2 failure): Uses `sys.exit("fork #2 failed: ...")` - plain text, NOT JSON
2. **Lines 250-254** (async directory creation): Uses `"failed": 1` (integer) instead of `"failed": True` (boolean)
3. **Line 326** (timeout): Uses `sys.exit(0)` - no JSON output, no child PID

## Candidate Fixes
1. Fork #2 failure: Replace `sys.exit("fork #2 failed...")` with JSON output like fork #1
2. Async directory creation: Change `"failed": 1` to `"failed": True`
3. Timeout: Replace `sys.exit(0)` with JSON output including `child_pid`

## Verification
Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` after fixes.