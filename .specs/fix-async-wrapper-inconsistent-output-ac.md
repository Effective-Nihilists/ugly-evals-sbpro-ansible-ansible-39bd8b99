# Fix async_wrapper inconsistent output

## Context
`async_wrapper.py` produces inconsistent/incomplete JSON across exit paths (fork failure, dir creation failure, timeout, normal completion). The test `test_run_module` fails, likely due to a bytes/str mismatch when the monkeypatched `_get_interpreter` mock returns strings but the command list is bytes.

## Plan

- [ ] Fix `_run_module`: convert interpreter result to bytes so mixed str/bytes doesn't break `subprocess.Popen`
- [ ] Fix timeout path in `main()`: write `failed` result JSON with `ansible_job_id` and child PID to job file before exiting
- [ ] Fix fork-failure exception handler in `main()`: add `ansible_job_id` to the printed JSON
- [ ] Fix dir-creation-failure handler in `main()`: use `True` instead of `1` for `failed`, add `ansible_job_id`

## Verification
Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v` and confirm it passes.
