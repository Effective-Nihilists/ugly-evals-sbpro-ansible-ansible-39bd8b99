# async_wrapper diagnosis

## Symptom
Test `test_run_module` fails with:
```
assert jres.get('rc') == 0
AssertionError: assert None == 0
Result: {'failed': 1, 'msg': "[Errno 2] No such file or directory: '/usr/bin/python'", ...}
```

The module execution fails because `_get_interpreter` returns `None` when it should return the mocked interpreter `['/usr/bin/python']`.

## Root Cause
**Line 150** in `_run_module`:
```python
interpreter = _get_interpreter(cmd[0])
```

- Line 148: `cmd = [to_bytes(c, errors='surrogate_or_strict') for c in shlex.split(wrapped_cmd)]` converts the command list to bytes
- Line 150: passes `cmd[0]` (a bytes path) to `_get_interpreter`
- `_get_interpreter` at line 112-117 calls `open(module_path, 'rb')` which on Python 3 returns `None` when given a bytes path (type mismatch)
- Result: `interpreter` is `None`, so the subprocess uses the original module path as executable (which fails)

## Candidate Fixes

**Option A (fix `_run_module`):** Change line 150 to pass the string path instead of bytes:
```python
interpreter = _get_interpreter(shlex.split(wrapped_cmd)[0])
```
- Pros: Minimal, surgical fix; passes the original string to `_get_interpreter`
- Cons: Slight redundancy (shlex.split called again)

**Option B (fix `_get_interpreter`):** Handle bytes input in `_get_interpreter`:
```python
def _get_interpreter(module_path):
    with open(module_path, 'rb') as module_fd:
        head = module_fd.read(1024)
        if head[0:2] != b'#!':
            return None
        return head[2:head.index(b'\n')].strip().split(b' ')
```
Could add `if isinstance(module_path, bytes): module_path = os.fsdecode(module_path)` at the start.
- Pros: Makes `_get_interpreter` more robust for callers that pass bytes
- Cons: More code changes, affects a shared utility function

## Recommended Fix
**Option A** — change line 150 in `_run_module` to use the original string path. This is the smallest fix that resolves the test failure.