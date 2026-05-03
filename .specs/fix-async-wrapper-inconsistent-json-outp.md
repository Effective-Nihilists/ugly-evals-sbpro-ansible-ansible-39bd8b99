# Fix async_wrapper inconsistent JSON output across exit paths

## Diagnosis

The `async_wrapper` module produces inconsistent JSON output across different exit paths:

1. **Inconsistent `failed` type**: Some paths use `"failed": 1` (integer), others use `"failed": True` (boolean) — line 180, 192, 240 vs line 336.

2. **Inconsistent field names**: Error paths use `"outdata"` (line 184) vs `"data"` (line 194) for the same data.

3. **No structured output on timeout**: When the watcher process kills the child on timeout (lines 309-316), it exits without writing any result to the job file — the initial `{"started": 1}` status remains indefinitely.

## Plan

- [ ] Fix `failed` type: change `"failed": 1` to `"failed": True` in all error paths
- [ ] Fix field name: change `"data"` to `"outdata"` in line 194 for consistency
- [ ] Fix timeout path: write structured JSON result to job file when timeout kills the child

## Verification

- `python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -x -v` passes
- Visual inspection confirms all error paths use consistent types and field names
