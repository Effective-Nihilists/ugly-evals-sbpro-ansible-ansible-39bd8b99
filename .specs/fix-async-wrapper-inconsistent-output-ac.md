# Fix async_wrapper inconsistent output across exit paths

## Context
The `async_wrapper` module in `lib/ansible/modules/async_wrapper.py` produces inconsistent or incomplete JSON output across different exit paths. Fork failures emit plain text, some error paths miss `ansible_job_id`, timeouts produce no structured output. The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` currently fails.

## Plan

- [ ] Investigate the exact test failure by running it
- [ ] Fix `_run_module` to ensure consistent JSON output in the job file
- [ ] Fix `main()` fork error paths to emit JSON instead of plain text
- [ ] Add `ansible_job_id` to all error JSON outputs in `main()`
- [ ] Add child PID context to timeout results
- [ ] Verify the test passes

## Verification
- `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` exits 0
- All JSON outputs from `async_wrapper` are well-formed and include consistent fields (`failed`, `msg`, `ansible_job_id`) where applicable
