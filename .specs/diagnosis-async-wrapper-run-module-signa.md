# Fix Applied: `_run_module` return statements

## What was changed
Added `return result` to each code path in `_run_module` in `lib/ansible/modules/async_wrapper.py`:
- Line 177: normal completion path
- Line 190: OSError/IOError handler
- Line 202: ValueError/Exception handler

## Verification
`pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` → **PASSED**