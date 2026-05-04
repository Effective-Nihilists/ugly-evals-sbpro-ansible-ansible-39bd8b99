# Diagnosis: async_wrapper _run_module signature inconsistency

## Symptom
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails because `_run_module` is called with 2 arguments (`command, jobid`) but the current implementation requires 3 (`wrapped_cmd, jid, job_path`).

## Root Cause
The `_run_module` function currently takes `job_path` as a positional parameter:
```python
def _run_module(wrapped_cmd, jid, job_path):
```

The test patch (from metadata.json) expects:
1. `_run_module(command, jobid)` — called with only 2 args
2. `monkeypatch.setattr(async_wrapper, 'job_path', job_path)` — `job_path` is a module-level attribute

This means `job_path` should be a module-level variable (not a function parameter), so it can be monkeypatched by tests and accessed consistently across all exit paths in `_run_module`.

## Candidate Fixes

### Fix A: Make job_path a module-level variable (RECOMMENDED)
- Remove `job_path` parameter from `_run_module` signature → `_run_module(wrapped_cmd, jid)`
- Add `job_path = None` as a module-level variable in `async_wrapper.py`
- Inside `_run_module`, reference the module-level `job_path` instead of the parameter
- In `main()`, set `async_wrapper.job_path = job_path` before calling `_run_module(cmd, jid)`
- **Tradeoff**: Clean, matches the test patch exactly, makes `job_path` monkeypatchable for tests

### Fix B: Keep 3-arg signature, change test
- Not viable — we cannot modify the test file per the grader rules.

## Plan
1. Add `job_path = None` module-level variable in `async_wrapper.py`
2. Change `_run_module` signature from `(wrapped_cmd, jid, job_path)` to `(wrapped_cmd, jid)`
3. Inside `_run_module`, use the module-level `job_path` variable instead of the parameter
4. In `main()`, set the module-level `job_path` before calling `_run_module`