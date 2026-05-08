# Fix async_wrapper inconsistent output across exit paths

## Context
The `async_wrapper` module produces inconsistent/incomplete JSON output across different exit paths (fork failure, timeout, directory creation failure, normal completion). The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` is failing.

## Plan
- [ ] Read the test file to understand what it expects
- [ ] Read the async_wrapper source to understand current behavior
- [ ] Fix the source to produce consistent JSON output across all exit paths

## Verification
- `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -x` passes
