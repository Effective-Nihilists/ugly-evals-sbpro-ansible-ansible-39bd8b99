# async_wrapper bug fix

## Context
The `async_wrapper._run_module` function fails when running the test because `_get_interpreter` receives a **bytes** path instead of a **string** path.

## Root Cause
On line 150: `interpreter = _get_interpreter(cmd[0])`
- Line 148 converts the command to bytes: `cmd = [to_bytes(c) for c in shlex.split(wrapped_cmd)]`
- `_get_interpreter` calls `open(module_path, 'rb')` which on Python 3 returns `None` when given bytes
- Result: `interpreter` is `None`, so the mock return value is never used

The `_get_interpreter` function needs to be called with the **original string path** (`wrapped_cmd.split()[0]`) not the bytes-converted path (`cmd[0]`).

## Fix
Change line 150 from:
```python
interpreter = _get_interpreter(cmd[0])
```
to:
```python
interpreter = _get_interpreter(shlex.split(wrapped_cmd)[0])
```

This passes a string path to `_get_interpreter`, allowing it to correctly read the shebang and return the interpreter.

## Verification
```bash
PYTHONPATH="$(pwd)/lib" python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v
```
Test should pass.