# Diagnosis: async_wrapper `_run_module` signature mismatch and output inconsistencies

## Symptom

When the SWE-bench Pro Docker image applies `test_patch` and runs `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module`, the test fails with:

```
TypeError: _run_module() missing 1 required positional argument: 'job_path'
```

## Root Cause (primary — blocking)

The `test_patch` in `eval/metadata.json` modifies the test to:
1. Call `_run_module(command, jobid)` with **2 positional arguments** (not 3)
2. Set `async_wrapper.job_path` via `monkeypatch` before the call

The current **source code** has `def _run_module(wrapped_cmd, jid, job_path):` — a 3-parameter signature — so calling it with 2 args raises `TypeError`.

The fix: change `_run_module` to take 2 parameters `(wrapped_cmd, jid)` and read `job_path` from the module's attribute (`sys.modules[__name__].job_path`). In `main()`, set this attribute before calling `_run_module`.

## Root Cause (secondary — consistency per ticket)

The TICKET requires uniform JSON output across all exit paths. The source has these inconsistencies:

| Location | Bug | Fix |
|---|---|---|
| Line 181 `except (OSError, IOError)` | `"failed": 1` (int) | `"failed": True` (bool) |
| Line 192 `except (ValueError, Exception)` | `"failed": 1` (int), `"data"` key | `"failed": True`, `"outdata"` for consistency |
| Line 241 `except Exception` in `main()` | `"failed": 1` (int) | `"failed": True` (bool) |
| Line 175 success path | Missing `ansible_job_id` | Add `result['ansible_job_id'] = jid` |

## Plan

- [ ] Change `_run_module` signature from `(wrapped_cmd, jid, job_path)` to `(wrapped_cmd, jid)`, read `job_path` via `sys.modules[__name__].job_path`
- [ ] In `main()`, set `sys.modules[__name__].job_path = job_path` before calling `_run_module(cmd, jid)`
- [ ] Add `result['ansible_job_id'] = jid` to success path in `_run_module`
- [ ] Change all `"failed": 1` to `"failed": True` (bool consistency)
- [ ] Change `"data"` to `"outdata"` in the `except (ValueError, Exception)` block for consistency

## Verification

Apply the test_patch to the test file, then run `python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` with `PYTHONPATH=lib`. The test must pass.
