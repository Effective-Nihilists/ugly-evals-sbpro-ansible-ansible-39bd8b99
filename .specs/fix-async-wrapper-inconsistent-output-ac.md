# Fix `async_wrapper` inconsistent output across exit paths

## Context
The `async_wrapper` module produces inconsistent or incomplete JSON output across different exit paths (normal completion, fork failures, timeouts, async directory creation errors). The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` is currently failing.

## Plan
- [ ] Explore the async_wrapper source and test to understand current behavior
- [ ] Fix the source to produce consistent JSON output across all exit paths
- [ ] Run the failing test to verify the fix

## Verification
Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` and confirm it passes.
