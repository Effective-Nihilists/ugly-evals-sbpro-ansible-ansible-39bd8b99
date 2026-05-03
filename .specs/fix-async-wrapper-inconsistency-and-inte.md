# Diagnosis: async_wrapper test_run_module failure

## Symptom

`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails in the SWE-bench Docker environment with these assertions failing:
- `jres.get('rc') == 0` → `None == 0` → `False`
- `jres.get('stderr') == 'stderr stuff'` → `'' == 'stderr stuff'` → `False`

The test DOES pass on macOS because `/usr/bin/python` exists there.

## Root Cause

In `_run_module()`, the test monkeypatches `_get_interpreter` to return `['/usr/bin/python']`. The code does:

```python
interpreter = _get_interpreter(cmd[0])
if interpreter:
    cmd = interpreter + cmd
```

Then `subprocess.Popen(['/usr/bin/python', module_script], ...)` is called. In the SWE-bench Docker environment, `/usr/bin/python` does not exist, so `Popen` raises `OSError`.

The `except (OSError, IOError):` handler writes a result dict with `{"failed": 1, ...}` — crucially, it does NOT contain an `"rc"` key. When the test reads the job file and calls `jres.get('rc')`, it gets `None`, and `None == 0` is `False`.

## Additional Inconsistencies Found (same file)

1. **`"data"` vs `"outdata"`** — The `except (ValueError, Exception):` handler uses key `"data"` while the `except (OSError, IOError):` handler uses key `"outdata"`. These should be consistent.

2. **`"failed": 1` (int) vs `"failed": True` (bool)** — In `main()`:
   - Argument check uses `"failed": True` (line 211)
   - Temp dir error handler uses `"failed": 1` (line 244) — inconsistent
   - General `except Exception:` handler uses `"failed": True` (line 337)

## Candidate Fixes

### Fix 1 (primary — fixes test failure): Interpreter existence check
Add a check after `_get_interpreter` returns: if `interpreter[0]` doesn't exist on the filesystem, fall back to `sys.executable` (the current Python interpreter). This is the direct cause of the test failure.

### Fix 2: Standardize `"data"` → `"outdata"`
In the `except (ValueError, Exception):` handler, change `"data"` to `"outdata"` for consistency with the OSError handler. Minor but matches ticket's call for "consistent field names."

### Fix 3: Standardize `"failed"` field type in `main()`
Change `"failed": 1` to `"failed": True` in the temp dir error handler of `main()` (line 244) to match the boolean type used in the other error paths.
