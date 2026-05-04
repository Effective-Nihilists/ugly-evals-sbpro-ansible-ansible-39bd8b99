# Fix async_wrapper _run_module signature

## Context
The `async_wrapper` module's `_run_module` function currently takes 3 args `(wrapped_cmd, jid, job_path)`, but the test expects it to take only 2 args `(wrapped_cmd, jid)` and use a module-level `job_path` variable instead.

## Plan
- [ ] Add module-level `job_path` variable to `async_wrapper.py`
- [ ] Change `_run_module` signature from `(wrapped_cmd, jid, job_path)` to `(wrapped_cmd, jid)`, referencing module-level `job_path`
- [ ] In `main()`, set module-level `job_path` before calling `_run_module`
- [ ] Update `_run_module(cmd, jid, job_path)` call to `_run_module(cmd, jid)`

## Verification
- Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module`