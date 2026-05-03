# Diagnosis: test_run_module failure in async_wrapper

## Context
Repo: ansible/ansible, base commit 8502c2302871e35e59fb7092b4b01b937c934031
Failing test: `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module`

## Symptom
The test calls `async_wrapper._run_module(command, jobid, jobpath)` and expects the result written to the job file to contain `rc == 0` and `stderr == 'stderr stuff'`. Instead, the job file contains:
```json
{"failed": 1, "cmd": "...", "msg": "[Errno 2] No such file or directory: '/usr/bin/python'", "outdata": "", "stderr": "", "ansible_job_id": 0}
```
`jres.get('rc')` returns `None`, causing `assert None == 0` to fail.

## Root Cause
The test monkeypatches `_get_interpreter` to return `['/usr/bin/python']`. In `_run_module()` at `lib/ansible/modules/async_wrapper.py:152-153`, this interpreter is prepended to the command:
```python
interpreter = _get_interpreter(cmd[0])
if interpreter:
    cmd = interpreter + cmd
```
This produces `cmd = ['/usr/bin/python', b'/path/to/script']`. `subprocess.Popen(cmd, ...)` fails because `/usr/bin/python` does not exist on the test system (macOS/Ubuntu 22.04+ removed the bare `python` symlink). The `OSError` is caught by the handler at lines 178-188, which writes a result dict **without an `rc` key**, only `failed`, `cmd`, `msg`, `outdata`, `stderr`, `ansible_job_id`.

The ticket's broader issue is that `async_wrapper` produces inconsistent output across exit paths — error handlers omit `rc` and other fields present in the success path.

**No argument mismatch**: `_run_module(wrapped_cmd, jid, job_path)` — 3 parameters, called with 3 arguments. Verified via inspect.

## Candidate Fixes
1. **Add `rc` to all error result dicts** — ensure `failed=1` error results also include `rc: 1`. Makes output consistent across exit paths per the ticket. Test expects `rc == 0`, so this is needed but not sufficient alone.

2. **Fix the subprocess invocation** — the real issue is that `cmd = interpreter + cmd` produces a mixed str/bytes list and the interpreter path is hardcoded mock value. The fix should make the OSError/Exception handlers include `rc` so that the output is always consistent. Then, on systems where `/usr/bin/python` exists, the test will hit the success path and pass normally.

## Verification Plan
After fix: run `PYTHONPATH=lib uv run pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` and confirm it passes.
