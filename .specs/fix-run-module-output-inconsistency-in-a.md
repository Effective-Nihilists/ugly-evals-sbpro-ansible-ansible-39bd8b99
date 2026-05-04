# Fix `_run_module` output inconsistency in async_wrapper

## Context

The `async_wrapper` module's `_run_module` function produces inconsistent JSON output across different exit/error paths:
- `"failed": 1` (integer) used in error paths vs `"failed": True` (boolean) in some success module outputs
- `"data": outdata` in ValueError handler vs `"outdata": outdata` in OSError handler (inconsistent field name)
- Missing `ansible_job_id` in success path result (initial file write has it, but result overwrites it)

## Plan

- [ ] Fix `OSError/IOError` handler: change `"failed": 1` to `"failed": True`
- [ ] Fix `ValueError/Exception` handler: change `"failed": 1` to `"failed": True` and `"data": outdata` to `"outdata": outdata`
- [ ] Add `result['ansible_job_id'] = jid` in the normal success path of `_run_module`
- [ ] Run the test to verify it still passes

## Verification

Run `python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v` — must pass with exit 0.
