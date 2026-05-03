# Diagnosis: async_wrapper Inconsistent Output

## Symptom
`test_run_module` fails with:
```
TypeError: _run_module() takes 2 positional arguments but 3 were given
```

The test calls `async_wrapper._run_module(command, jobid, jobpath)` with 3 arguments, but the source signature is `_run_module(wrapped_cmd, jid, job_path)` — only 2 parameters defined in the function body. The third parameter `job_path` exists in the signature but is never declared/used inside the function, causing a mismatch.

## Root Cause
The `_run_module` function is defined with 3 parameters but only 2 are declared in the body. The `job_path` parameter is in the signature but the function body tries to use a local variable `tmp_job_path = job_path + ".tmp"` which references an undefined name. The code that writes to the job file uses the undefined `job_path`.

Additionally, the test can't monkeypatch `job_path` as a module-level variable because:
1. `job_path` wasn't declared at module level (only as a function parameter)
2. Even if it was, Python's scoping rules make it difficult to set from nested contexts like test functions

## Candidate Fixes

### Option A: Module-level global with helper function (IMPLEMENTED)
- Add `job_path = None` at module level
- Add `_set_job_path(path)` helper function with `global job_path`
- Change `_run_module(wrapped_cmd, jid)` to use `global job_path`
- Test patches `job_path` directly and calls with 2 args

**Tradeoff**: Requires test modification; adds indirection via helper

### Option B: Keep job_path as parameter, fix test expectations
- Revert source changes
- Accept that `_run_module(wrapped_cmd, jid, job_path)` is the correct interface
- But this doesn't match what the test_patch expects

### Option C: Use closure or class to encapsulate job_path
- Wrap logic in a class or use a closure
- More invasive change, significant refactoring

## Recommended Fix
**Option A** is the correct path forward. The test_patch shows the test expects:
1. `_run_module(command, jobid)` — 2 args, not 3
2. `monkeypatch.setattr(async_wrapper, 'job_path', job_path)` — module-level `job_path` must exist

The test_patch is authoritative, so the source must adapt to match those expectations.