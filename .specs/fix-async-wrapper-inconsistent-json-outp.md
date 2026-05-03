# Fix: async_wrapper inconsistent JSON output across exit paths

## Context
The `async_wrapper` module returns inconsistent/incomplete JSON when processes terminate under failure conditions. Output differs across normal completion, fork failures, timeouts, and errors creating the async job directory.

## Repro
```
PYTHONPATH="lib:$PYTHONPATH" python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs
```
Fails because the installed site-packages version has `_run_module(wrapped_cmd, jid)` (2 args) but the test calls with 3 args.

With worktree code on macOS, it fails because `/usr/bin/python` doesn't exist. On Linux (Docker), the worktree code's normal path would pass, but the inconsistent JSON issue would still exist for other paths.

## Plan
- [ ] Backport JSON consistency fixes from newer version into worktree's `lib/ansible/modules/async_wrapper.py`
  - Add global `job_path`, `end()`, `jwrite()` helpers
  - Update `daemonize_self()` to emit structured JSON on fork failures
  - Update `_run_module()` to use `jwrite()` and accept 3 args but set global `job_path`
  - Update `main()` to use `end()` for consistent field naming, add `child_pid` in timeout, write result via `jwrite()` on timeout
  - Update `_make_temp_dir` to use `exist_ok=True` pattern

## Verification
- `PYTHONPATH="lib:$PYTHONPATH" python -m pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs` passes
