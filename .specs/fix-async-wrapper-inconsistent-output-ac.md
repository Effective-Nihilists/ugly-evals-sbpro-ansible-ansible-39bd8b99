# Fix `async_wrapper` inconsistent output across exit paths

## Context

The `async_wrapper` module in `lib/ansible/modules/async_wrapper.py` produces inconsistent JSON output across its different exit paths (normal completion, fork failures, timeouts, async-dir creation errors). Field names, presence of keys, and value types vary between code paths, making async job handling unreliable.

## Repro

Run: `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module`

The test validates that `_run_module` writes a job file with consistent fields (`rc`, `stderr`, etc.). The underlying code has inconsistencies that cause unreliable behavior across exit paths.

## Plan

- [ ] In `_run_module`, make the two exception handlers use consistent field names: change `"outdata"` key in the `OSError/IOError` handler (line 184) to `"data"` to match the `ValueError/Exception` handler (line 194).
- [ ] In `_run_module`, ensure the success path includes `ansible_job_id` in the result dict (currently missing; error paths include it).
- [ ] In `main()`, add `ansible_job_id` to the async-dir creation failure JSON (line 240-244) for consistency with other error paths.
- [ ] In `main()`, change `"failed": True` (boolean) in the general exception handler (line 337) to `"failed": 1` (integer) to match all other error paths that use integer `1`.

## Verification

- `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes
- All exception handlers in `_run_module` use the same field names (`data`, not `outdata`)
- All error JSON outputs include `ansible_job_id`
- All `failed` fields use integer `1` consistently (not boolean `True`)