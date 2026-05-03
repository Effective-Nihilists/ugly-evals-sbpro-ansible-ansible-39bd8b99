# async_wrapper — Fix Inconsistent Output

## Symptom
Test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails because `_run_module` produces inconsistent JSON across exit paths. A stale .pyc from another worktree caused import errors; after deleting `lib/ansible/modules/__pycache__/async_wrapper.cpython-312.pyc`, the source is clean (345 lines, no SyntaxError).

## Root Cause
Two inconsistencies in `_run_module`:
1. **Missing `ansible_job_id` in success path** (line ~176): Added only in exception handlers (lines 188, 199), not in the success path.
2. **Inconsistent field name `data` vs `outdata`**: OSError handler uses `outdata` (line 185); ValueError/Exception handler used `data` (was line 195).

## Fixes Applied
1. Added `result['ansible_job_id'] = jid` at line 176 before `jobfile.write()` — makes success path consistent with exception handlers.
2. Changed `data` to `outdata` in the ValueError/Exception handler (line 195) — standardizes field name across all failure paths.

## Verification
`python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v` must pass (0 failures).