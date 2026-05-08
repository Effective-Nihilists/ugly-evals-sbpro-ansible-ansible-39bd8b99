# Fix async_wrapper._run_module to return result

## Context
The `_run_module` function in `lib/ansible/modules/async_wrapper.py` writes results to a job file but does not return the result dictionary. The test `test_run_module` calls `_run_module` and assigns its return value to `res`. While the current test doesn't check `res`, the function should return the result for consistency and to match expected behavior.

## Plan
- [ ] Add `return result` at the end of `_run_module` in `lib/ansible/modules/async_wrapper.py`

## Verification
- Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` and confirm it passes
