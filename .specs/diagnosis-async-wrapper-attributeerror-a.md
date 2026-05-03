# Diagnosis: async_wrapper AttributeError and Signature Mismatch

## Symptom

Test `test_run_module` in `test/units/modules/test_async_wrapper.py` fails with:
```
AttributeError: <module 'ansible.modules.async_wrapper'> has no attribute 'job_path'
```

The test_patch modifies the test to:
1. Call `monkeypatch.setattr(async_wrapper, 'job_path', job_path)` — requires a module-level `job_path`
2. Call `async_wrapper._run_module(command, jobid)` — 2 args, but original has 3

## Root Cause (verified)

Three separate bugs in `lib/ansible/modules/async_wrapper.py`:

1. **No module-level `job_path` variable** — test cannot monkeypatch an attribute that doesn't exist at module scope
2. **Wrong `_run_module` signature** — original is `_run_module(wrapped_cmd, jid, job_path)` with 3 args; test calls with 2 args
3. **Local variable shadowing** — in `main()`, `job_path = os.path.join(jobdir, jid)` creates a local that shadows any module-level name; even with a module-level `job_path`, `_run_module` would see `None`

## Candidate Fixes

### Fix A: Module-level job_path + global declaration (chosen)
- Add `job_path = None` at module level (line ~29)
- Add `global job_path` in `main()` before the assignment (line ~237)
- Change `_run_module(wrapped_cmd, jid, job_path)` → `_run_module(wrapped_cmd, jid)`, using module-level `job_path`
- Update call site to 2 args

**Tradeoffs**: Clean interface, testable, backward-compatible. Applied.

### Fix B: Pass job_path as argument (rejected)
- Keep 3-arg `_run_module` and pass `job_path` from each call site
- Downside: requires changing every call site, more invasive

### Fix C: Convert to class (rejected)
- Wrap in a class with `job_path` as instance attribute
- Downside: significant restructuring, unnecessary for this fix

## Verification

- Direct Python test confirms: with `/tmp/python` and mocked `_get_interpreter`, `job_path` correctly reaches `_run_module` and the job result file gets `{'rc': 0}`
- Local pytest fails only because `/usr/bin/python` doesn't exist in this macOS environment (only `/usr/bin/python3`); Docker image has `/usr/bin/python`