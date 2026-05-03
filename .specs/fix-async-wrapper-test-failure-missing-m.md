# Fix `async_wrapper` test failure: missing module-level `job_path`

## Context
The test `test/units/modules/test_async_wrapper.py::test_run_module` has a patch (from `eval/metadata.json`) that modifies the test to:
1. Call `_run_module(command, jobid)` with 2 arguments (removing `job_path`)
2. Set `monkeypatch.setattr(async_wrapper, 'job_path', job_path)` 

## Symptom
```
AttributeError: <module 'ansible.modules.async_wrapper'> has no attribute 'job_path'
```

## Root cause
The source `lib/ansible/modules/async_wrapper.py` needs two changes to match the test patch:
1. No module-level `job_path` variable exists — the test tries `monkeypatch.setattr(async_wrapper, 'job_path', ...)` and fails
2. `_run_module(wrapped_cmd, jid, job_path)` takes 3 params — the test calls it with 2

## Fix
- [ ] Add `job_path = None` at module level (after the imports, before `PY3 = ...`)
- [ ] Change `_run_module(wrapped_cmd, jid, job_path)` → `_run_module(wrapped_cmd, jid)` — use the module-level `job_path` inside
- [ ] In `main()`, declare `global job_path` so the computed `job_path = os.path.join(jobdir, jid)` assigns to the module-level variable, making it accessible to the grandchild process that calls `_run_module`
- [ ] Update the `_run_module(cmd, jid, job_path)` call in `main()` to `_run_module(cmd, jid)`

## Verification
- [ ] Run `PYTHONPATH="lib:$PYTHONPATH" uv run python -m pytest test/units/modules/test_async_wrapper.py -v` — must pass
