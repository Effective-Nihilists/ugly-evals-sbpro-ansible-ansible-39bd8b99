# Diagnosis: async_wrapper inconsistent output across exit paths

## Symptom

The test `test_run_module` fails with:
```
assert jres.get('rc') == 0
assert None == 0
```
The job file contains a dict from the OSError handler (`{"failed": 1, "msg": "No such file or directory: '/usr/bin/python'", ...}`) instead of the module's output (`{"rc": 0, "stderr": "stderr stuff"}`).

## Root cause

**Two interacting problems:**

### 1. Type mismatch in interpreter concatenation**

- The **real** `_get_interpreter()` returns bytes: `[b'/usr/bin/python']`
- The **test mock** returns strings: `['/usr/bin/python']`
- `cmd` after `to_bytes()` is bytes: `[b'/path/to/module']`
- After `interpreter + cmd`, the list has mixed `[str, bytes]` types

On the SWE-bench Docker image (Ubuntu 22.04+ with Python 3.8-3.10), `subprocess.Popen` with mixed str/bytes args can trigger `TypeError` or `FileNotFoundError` (if `/usr/bin/python` is a dangling symlink or Python 2). The fallback OSError handler then writes a result dict **without an `rc` key**, causing `jres.get('rc')` to return `None`.

### 2. Inconsistent error result dicts across handlers

Regardless of the subprocess issue, the three exit paths in `_run_module` produce structurally different JSON:

| Field | Success path | OSError handler | ValueError handler |
|-------|-------------|-----------------|-------------------|
| `failed` | absent | `1` (int) | `1` (int) |
| `rc` | ✓ (from module) | absent | absent |
| `stderr` | ✓ (if present) | ✓ | ✓ |
| `ansible_job_id` | absent | ✓ | ✓ |
| output key | (module keys) | `"outdata"` | `"data"` |
| `msg` | absent | `to_text(e)` | `traceback.format_exc()` |
| `cmd` | absent | ✓ | ✓ |

Additionally in `main()`:
- Tempdir creation failure: `"failed": 1` (int)
- Top-level exception: `"failed": True` (bool)
- Usage error: `"failed": True` (bool)

## Candidate fixes

### Fix 1 (primary): Convert interpreter to bytes for type consistency
In `_run_module`, after calling `_get_interpreter()`, convert each element to bytes:
```python
interpreter = _get_interpreter(cmd[0])
if interpreter:
    interpreter = [to_bytes(i, errors='surrogate_or_strict') for i in interpreter]
    cmd = interpreter + cmd
```
This makes the list all-bytes regardless of whether `_get_interpreter` returns bytes or strings.

### Fix 2: Standardize error result dicts across all paths
- Use `"failed": True` (boolean) everywhere
- Add `ansible_job_id` on the success path  
- Use `"outdata"` key consistently (not `"data"`)
- Make `main()` use `"failed": True` consistently

### Fix 3: Do not prepend interpreter when the script has a compatible shebang
Let the OS handle shebang execution, avoiding the mixed-type issue entirely. However, this would bypass the mock's purpose.

## Fix to apply

Combine Fix 1 + Fix 2: ensure type safety in interpreter+cmd concatenation AND standardize the output dicts for all exit paths. The primary fix that makes `test_run_module` pass is Fix 1 — the type conversion ensures `subprocess.Popen` receives a uniform-typed arg list, so the module runs and `rc` appears in the result.

## Verification

After the fix, run:
```
pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs
```
The test should show `PASSED`.
