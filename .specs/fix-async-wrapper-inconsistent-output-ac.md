# Fix async_wrapper inconsistent output across exit paths

## Context
The `_run_module` function in `lib/ansible/modules/async_wrapper.py` produces inconsistent JSON output across different code paths (success, OSError, ValueError). This makes async job handling unreliable.

## Plan
- [ ] Fix `_run_module` to use consistent `failed: True/False` (boolean) everywhere
- [ ] Fix `_run_module` to use consistent field name `outdata` (not `data`)
- [ ] Always include `ansible_job_id` in the result dict
- [ ] Always include `stderr` in the result dict (even if empty)
- [ ] Add `finished: 1` to the result on success
- [ ] Verify the test still passes

## Verification
- `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` should pass
