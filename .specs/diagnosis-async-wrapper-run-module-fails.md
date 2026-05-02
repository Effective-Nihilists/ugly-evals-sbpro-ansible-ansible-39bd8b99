# Diagnosis: async_wrapper _run_module fails when shebang interpreter doesn't exist

## Symptom
`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails:
- `jres.get('rc')` returns `None` instead of `0`
- The job file contains `{'failed': 1, 'msg': "[Errno 2] No such file or directory: '/usr/bin/python'"}` instead of the module result

## Root Cause
The `_run_module` function calls `_get_interpreter(cmd[0])` which returns the shebang interpreter from the module script (e.g., `['/usr/bin/python']`). This interpreter list is unconditionally prepended to the command. If the shebang interpreter path (`/usr/bin/python`) doesn't exist on the system, `subprocess.Popen` raises `OSError`, which is caught by the error handler, producing a result dict without `rc` or `stderr` keys.

The SWE-bench Pro Docker image does not have the `python-is-python3` package installed, so `/usr/bin/python` doesn't exist — only `/usr/bin/python3` is present.

## Candidate Fixes

### Fix A — Fall back to `sys.executable` when shebang interpreter is missing (RECOMMENDED)
In `_run_module`, after `_get_interpreter` returns, check if the interpreter executable path exists via `os.path.exists()`. If it doesn't, use `sys.executable` as fallback:
- **Minimal change**: only touches the interpreter-picking logic
- **Preserves functionality**: non-Python shebangs (`/bin/bash`, `/usr/bin/ruby`) continue to work when their interpreters exist
- **Makes the test pass**: the mock returns `['/usr/bin/python']`, `os.path.exists` returns `False`, `sys.executable` is used instead

### Fix B — Use `sys.executable` unconditionally
Replace the entire interpreter-prepending logic with `sys.executable`:
- **More aggressive**: changes behavior for all scripts, not just when interpreter is missing
- **Breaks non-Python modules**: Bash/ruby scripts would be executed with Python interpreter

### Fix C — Retry with `sys.executable` on OSError
Catch the OSError in `_run_module` and retry with `sys.executable`:
- **Same net effect** as Fix A with more code complexity
- **Two subprocess attempts** on failure: wasteful and slower

## Verification
After applying Fix A:
1. `PYTHONPATH=lib:test pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` should pass
2. Reproducer at `/tmp/repro_async.py` (using shebang `#!/usr/bin/python3`) should continue to pass
3. Error paths in `_run_module` should still produce well-formed JSON with consistent field names
