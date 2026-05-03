# Diagnosis: async_wrapper _run_module Missing Parameter

## Symptom
Test `test_run_module` fails with:
```
TypeError: _run_module() takes 2 positional arguments but 3 were given
```
Test calls: `async_wrapper._run_module(command, jobid, jobpath)` — 3 args.
Function signature: `def _run_module(wrapped_cmd, jid)` — only 2 params.

## Root Cause
The `_run_module` function at `lib/ansible/modules/async_wrapper.py:129` has a **stub signature** — it only accepts `(wrapped_cmd, jid)` but the function body and callers use `job_path` as well:
- The function body references `job_path` internally (lines 131, 135, 136, 202)
- The call site in `main()` passes 3 args: `_run_module(cmd, jid, job_path)` (line 324)

The parameter is missing from the signature, making it a stub that needs to be filled in.

## Candidate Fix
Add `job_path` as the third parameter to `_run_module`:
```python
def _run_module(wrapped_cmd, jid, job_path):
```
No other changes needed — the body already uses `job_path` correctly.

## Verification
```bash
python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v
```
Expected: test passes (or next failure surfaces, confirming parameter mismatch is fixed).
