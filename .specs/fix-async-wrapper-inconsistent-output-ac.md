# Fix async_wrapper inconsistent output across exit paths

## Context

The `async_wrapper` module in `lib/ansible/modules/async_wrapper.py` produces inconsistent or incomplete JSON output across different exit paths (normal completion, fork failures, timeouts, directory creation errors). The eval harness checks that `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes after our changes.

## Plan

- [ ] Fix `_run_module` error paths: use boolean `True`/`False` for `failed` instead of integer `1`, ensure `ansible_job_id` is consistently included
- [ ] Fix `daemonize_self()` fork failure exits: print JSON instead of plain strings
- [ ] Fix watchdog timeout path in `main()` supervisor process: emit JSON with child PID context before `sys.exit(0)`
- [ ] Fix `_make_temp_dir` failure in `main()`: use `"failed": True` (boolean) instead of `"failed": 1` (integer)
- [ ] Verify test passes

## Acceptance criteria

1. `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes
2. All exit paths produce valid JSON with consistent field names
3. `failed` field uses `True`/`False` (booleans) consistently, not `1`/`0` integers
4. Timeout path includes useful context (child PID) in its JSON output