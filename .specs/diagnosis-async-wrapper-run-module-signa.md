# Diagnosis: async_wrapper _run_module signature mismatch

## Symptom
`TypeError: _run_module() missing 1 required positional argument: 'job_path'` — the test patch calls `_run_module(command, jobid)` with 2 args, but the current signature requires 3: `_run_module(wrapped_cmd, jid, job_path)`.

## Root Cause
The test patch (from eval/metadata.json) refactors `_run_module` to use a module-level `job_path` variable instead of a parameter. The current code:
- `_run_module(wrapped_cmd, jid, job_path)` takes `job_path` as a positional arg
- `main()` computes `job_path` locally and passes it as the 3rd arg

The test expects:
- A module-level `job_path` attribute (set via `monkeypatch.setattr(async_wrapper, 'job_path', job_path)`)
- `_run_module(command, jobid)` called with only 2 args, reading `job_path` from module scope

## Fix Plan
1. Add module-level `job_path = None` variable in `async_wrapper.py`
2. Change `_run_module` signature from `(wrapped_cmd, jid, job_path)` to `(wrapped_cmd, jid)`, referencing the module-level `job_path` instead of the parameter
3. In `main()`, assign to the module-level `job_path` before calling `_run_module`, and remove the 3rd arg from the call

## Verification
- `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes