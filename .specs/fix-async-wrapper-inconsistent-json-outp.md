# Fix async_wrapper inconsistent JSON output

## Context
The `async_wrapper` module produces inconsistent/incomplete JSON across different exit paths (fork failure, timeout, missing async directory, normal completion). The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` currently fails.

## Plan
- [ ] 1. Explore the async_wrapper source and test file to understand current behavior
- [ ] 2. Run the failing test to reproduce the failure
- [ ] 3. Identify inconsistent JSON output paths in the source code
- [ ] 4. Fix each exit path to produce consistent JSON with fields: `msg`, `failed`, `ansible_job_id`
- [ ] 5. Verify the fix by running the test

## Verification
- `cd test/units/modules && python -m pytest test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` passes
