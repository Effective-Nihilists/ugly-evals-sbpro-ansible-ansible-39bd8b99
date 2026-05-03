# Diagnosis: `_run_module` missing return statements

## Symptom
Test `test_run_module` failed with `TypeError: _run_module() takes 2 positional arguments but 3 were given` — caused by stale .pyc bytecode from a previous failed edit attempt. After clearing caches, the test passed but showed `res = None`.

## Root Cause
`_run_module` in `lib/ansible/modules/async_wrapper.py` had NO return statements. Every code path fell through to `return None`, so the function never returned the `result` dict it constructed and wrote to the job file.

## Fix Applied
Added `return result` after each code path in `_run_module`:
1. Normal completion (line 177)
2. OSError/IOError handler (line 190)
3. ValueError/Exception handler (line 202)

## Verification
`pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` → **PASSED**