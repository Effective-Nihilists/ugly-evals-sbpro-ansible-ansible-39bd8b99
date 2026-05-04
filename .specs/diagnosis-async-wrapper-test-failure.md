# Diagnosis: async_wrapper test failure

## Symptom
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with:
```
TypeError: _run_module() missing 1 required positional argument: 'job_path'
```

The test calls `_run_module(command, jobid)` with 2 positional arguments at line 50, but the function signature requires 3 arguments.

## Root Cause
The `_run_module` function in `lib/ansible/modules/async_wrapper.py` has `job_path` as a required positional parameter. The test expects to call it with just 2 arguments (command and jobid), relying on a module-level `job_path` variable that gets monkeypatched. The signature mismatch causes the test to fail.

## Candidate Fixes

1. **Make job_path optional with default None** (preferred):
   - Change `def _run_module(wrapped_cmd, jid, job_path)` to `def _run_module(wrapped_cmd, jid, job_path=None)`
   - Add module-level `job_path = None` 
   - Inside the function, use the passed value or fall back to the module-level variable
   - This maintains backward compatibility while allowing the test to work

2. **Alternative: Pass job_path in test** (not allowed - cannot modify test per TICKET.md)

## Verification
After the fix, run: `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v`
Expected: test passes