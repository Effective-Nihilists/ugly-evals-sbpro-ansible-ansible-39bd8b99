# Fix `async_wrapper` inconsistent output across exit paths

## Context

The `async_wrapper` module produces inconsistent or incomplete JSON output across different exit paths. The SWE-bench grader checks `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` which must pass after fixes.

## Plan

- [ ] Fix `daemonize_self` fork failures to emit structured JSON via `sys.exit(json.dumps(...))` instead of free-form text strings
- [ ] Fix the timeout path in the supervisor process (`sub_pid` branch) to write a proper timeout result to the job file before exiting
- [ ] Make `failed` field consistent — use `True`/`False` (bool) everywhere instead of mixing `1`/`True`
- [ ] Make `started`/`finished` fields use `True`/`False` consistently
- [ ] Filter non-JSON output from all paths; ensure only one JSON object is emitted per process

## Non-goals

- Do not modify test files
- Do not change architecture or public API
- Do not touch the PowerShell async_wrapper

## Acceptance criteria

1. `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes
2. All exit paths in `_run_module` produce consistent JSON with bool `failed` field
3. Fork failures in `daemonize_self` produce JSON instead of free-form text
4. Timeout path writes a proper result to the job file

## Verification

```bash
pytest test/units/modules/test_async_wrapper.py -v 2>&1
```
