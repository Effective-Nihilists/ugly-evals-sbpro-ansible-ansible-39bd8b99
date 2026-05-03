# Diagnosis: async_wrapper inconsistent JSON output

## Symptom
The `async_wrapper` module produces inconsistent or incomplete JSON output across different exit paths:
- Some paths use `"failed": True` (boolean) while others use `"failed": 1` (integer)
- `ansible_job_id` is missing from several error and success paths
- Fork failures in `daemonize_self()` output unstructured text instead of JSON

## Root cause
Multiple code paths in `_run_module()` and `main()` independently construct result dictionaries without following a consistent schema:

| Path | Location | Issue |
|------|----------|-------|
| `daemonize_self()` fork failure 1 | line 45-48 | `sys.exit("fork #1 failed: ...")` → plain text, no JSON |
| `daemonize_self()` fork failure 2 | line 60-62 | `sys.exit("fork #2 failed: ...")` → plain text, no JSON |
| `_run_module()` success | ~line 172 | Missing `ansible_job_id` in result |
| `_run_module()` OSError/IOError | ~line 190-198 | `"failed": 1` (int), `ansible_job_id` added via separate statement |
| `_run_module()` ValueError/Exception | ~line 200-209 | `"failed": 1` (int), `ansible_job_id` added via separate statement |
| `main()` _make_temp_dir error | ~line 249-256 | `"failed": 1` (int), missing `ansible_job_id` |

## Fix applied (3 areas)

### 1. `daemonize_self()` — replace plain text with JSON
Changed `sys.exit("fork #1 failed: ...")` to `print(json.dumps({"failed": True, "msg": "..."}))` + `sys.exit(1)`. Same for fork #2.

### 2. `_run_module()` — standardize all three exit paths
- **Success path**: added `result['ansible_job_id'] = jid` after `json.loads()`
- **OSError/IOError**: `"failed": 1` → `"failed": True`, moved `ansible_job_id` inline into dict
- **ValueError/Exception**: `"failed": 1` → `"failed": True`, moved `ansible_job_id` inline into dict

### 3. `main()` — fix _make_temp_dir error path
`"failed": 1` → `"failed": True`, added `"ansible_job_id": jid`

## Verification
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes:
```
python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs
```
