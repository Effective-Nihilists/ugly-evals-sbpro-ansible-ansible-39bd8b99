# Diagnosis: async_wrapper inconsistent exit paths

## Symptom

`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with:

```
assert None == 0
where None = {'ansible_job_id': 0, 'cmd': ..., 'failed': 1, 'msg': "[Errno 2] ... /usr/bin/python"}.get('rc')
```

The test creates a temp Python module, mocks `_get_interpreter` to return `['/usr/bin/python']`, calls `_run_module()`, then checks the job file for `rc == 0` and `stderr == 'stderr stuff'`. Neither is present because the subprocess never ran.

## Root cause

`_run_module` uses `_get_interpreter(cmd[0])` to determine which interpreter to invoke. In the test, the mock returns `['/usr/bin/python']`. When `/usr/bin/python` is absent from the system, `subprocess.Popen` raises `OSError(errno.ENOENT)`. The OSError handler writes a result dict with `failed: 1` and `msg` but **no `rc` key**. The test rightfully expects `rc: 0` and `stderr: 'stderr stuff'` which only exist on the success path.

The code has three additional structural issues:

1. **Inconsistent `failed` type**: OSError/ValueError handlers write `"failed": 1` (int) while `main()` writes `"failed": True` (bool).
2. **Inconsistent field names**: OSError handler uses `"outdata"`, ValueError handler uses `"data"` for the same data.
3. **Missing `ansible_job_id` on success path**: The success branch parses module JSON and writes it directly without adding `ansible_job_id`; error branches do add it.
4. **No fallback when interpreter missing**: If the shebang interpreter binary doesn't exist, `Popen` raises OSError with no graceful degradation.

## Candidate fixes

### Fix A: Interpreter fallback in `_run_module`
In `_run_module`, after `interpreter = _get_interpreter(cmd[0])`, check whether the first element of `interpreter` is executable. If not, replace with `sys.executable`. This makes the module robust against missing interpreters.

### Fix B: Consistent JSON in `_run_module`
- Change `"failed": 1` → `"failed": True` in both error handlers.
- Change `"data"` → `"outdata"` in ValueError handler.
- Add `result['ansible_job_id'] = jid` on success path.
- Ensure `result['rc']` is set when available (from module output on success, or explicit `rc` on errors).

### Fix C: Timeout result in `main`
On timeout (`remaining <= 0` in the supervisor process), write a structured JSON result to the job file containing `failed: True`, `msg` with timeout info, `ansible_job_id`, and child PID before `sys.exit(0)`.

### Chosen approach
Combine A + B. Fix A resolves the immediate test failure (interpreter not found). Fix B addresses the ticket's core complaint about inconsistent JSON. Fix C is for robustness but isn't tested by the failing test.
