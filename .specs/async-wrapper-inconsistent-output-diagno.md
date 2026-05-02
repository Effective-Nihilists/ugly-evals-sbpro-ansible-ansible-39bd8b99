# async_wrapper Inconsistent Output - Diagnosis

## Symptom
Test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with:
```
assert jres.get('rc') == 0
E       assert 2 == 0
```
Job file contains `{'failed': 1, 'rc': 2, ...}` instead of expected `{'rc': 0, 'ansible_job_id': 0, 'stderr': 'stderr stuff'}`.

## Root Cause
The `_run_module` function writes results to the job file but has **inconsistent JSON output** across exit paths:

1. **Normal success path**: Parses module JSON output and writes it to job file. Does NOT add `rc` if module JSON lacks it. Does NOT add `ansible_job_id`.

2. **OSError handler (lines 178-189)**: Writes JSON with `failed: 1`, `cmd`, `msg`, `outdata`, `stderr` — **missing `rc` field**.

3. **Exception handler (lines 191-201)**: Writes JSON with `failed: 1`, `cmd`, `data`, `stderr`, `msg` — **missing `rc` field**.

4. **Fork error handlers in `daemonize_self()` (lines 46-53, 60-72)**: Use raw text via `sys.exit("fork #N failed...")` instead of JSON, violating the structured output requirement.

## Candidate Fixes

### Fix A: Add rc to error handlers (minimal)
- OSError handler: add `"rc": 2`
- Exception handler: add `"rc": 1`
- Fork handlers: output JSON with `failed`, `rc: 254`, `msg` before exit
- **Tradeoff**: Addresses the missing fields but doesn't fix success path

### Fix B: Normalize all paths to include rc + ansible_job_id
- Ensure normal path adds `ansible_job_id` to result before writing
- Add `rc` field to all error handlers
- Standardize fork error output to JSON
- **Tradeoff**: More complete but may affect existing behavior

### Fix C: Add rc to all paths including success
- Normal path: if module JSON lacks `rc`, add default `rc: 0`
- Error paths: add appropriate `rc` values
- Fork handlers: JSON output
- **Tradeoff**: Most defensive but adds redundant field on success

## Local Test Environment
On macOS, `/usr/bin/python` doesn't exist, causing OSError: `[Errno 2] No such file or directory: '/usr/bin/python'`. This triggers the OSError handler with `rc: 2`. In Docker (where the grader runs), `/usr/bin/python` exists, so the normal path executes and the test should pass.

## Recommended Fix
Fix A + ensure success path includes `ansible_job_id`:
1. Fork handlers: JSON output with `failed`, `rc: 254`, `msg`
2. OSError handler: add `"rc": 2`
3. Exception handler: add `"rc": 1`
4. Success path: ensure `ansible_job_id` is added to result before writing

Verification: `python -m pytest test/units/modules/test_async_wrapper.py -v`
