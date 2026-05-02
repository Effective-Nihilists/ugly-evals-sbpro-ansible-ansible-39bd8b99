# Fix async_wrapper Inconsistent Output Across Exit Paths

## Context
The `async_wrapper` module returns inconsistent or incomplete information when processes terminate, especially under failure conditions. Different exit paths use different field names and omit expected fields like `rc`.

## Repro
Running `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails because:
1. Test mocks `_get_interpreter` to return `['/usr/bin/python']`
2. On systems without `/usr/bin/python`, subprocess.Popen fails with OSError
3. The OSError handler creates a result without `rc` field
4. Test expects `rc: 0` but gets `rc: None`

## Plan
- [ ] Add `rc` field to OSError/IOError exception handler in `_run_module`
- [ ] Add `rc` field to ValueError/Exception exception handler in `_run_module`
- [ ] Ensure consistent field naming across all exit paths
- [ ] Run test to verify fix

## Verification
Test should pass: `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs`
