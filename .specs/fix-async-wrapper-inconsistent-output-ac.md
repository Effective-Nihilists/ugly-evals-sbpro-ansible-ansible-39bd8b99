# Fix `async_wrapper` inconsistent output across exit paths

## Context

The `async_wrapper` module produces inconsistent/incomplete JSON output across different exit paths (fork failures, timeout, async directory creation failures, normal completion). The test `test_run_module` in `test/units/modules/test_async_wrapper.py` is currently failing.

## Plan

- [ ] Read the test file to understand what the test expects
- [ ] Read the `async_wrapper` source to understand current behavior
- [ ] Fix the source to produce consistent JSON output across all exit paths

## Verification

Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` to confirm the test passes.
