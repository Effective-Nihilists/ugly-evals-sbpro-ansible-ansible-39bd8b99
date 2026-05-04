# Fix async_wrapper _run_module signature

## Context
The `async_wrapper` module's `_run_module` function currently takes 3 parameters: `(wrapped_cmd, jid, job_path)`. The test patch changes the call to `_run_module(command, jobid)` (2 args) and monkeypatches `async_wrapper.job_path` as a module-level attribute. This means `job_path` should be a module-level variable, not a function parameter.

## Plan
- [ ] Add module-level `job_path = None` variable in `async_wrapper.py`
- [ ] Change `_run_module` signature from `(wrapped_cmd, jid, job_path)` to `(wrapped_cmd, jid)`, using module-level `job_path`
- [ ] In `main()`, set `async_wrapper.job_path` (module-level) before calling `_run_module`
- [ ] Update `_run_module(cmd, jid, job_path)` call in `main()` to `_run_module(cmd, jid)`

## Verification
- Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` and confirm it passes