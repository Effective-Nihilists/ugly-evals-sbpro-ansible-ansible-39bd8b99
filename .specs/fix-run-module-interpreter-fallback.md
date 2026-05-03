# Fix `_run_module` interpreter fallback

## Bug

`_run_module` unconditionally prepends the shebang interpreter to the command list. When the interpreter (e.g. `/usr/bin/python`) doesn't exist on the system — as is common on minimal Docker images and modern macOS — `subprocess.Popen` raises `OSError`, the error handler writes a result dict without `rc`, and the test fails with `assert jres.get('rc') == 0`.

## Plan

- [x] Add `os.path.exists` check on the interpreter path inside `_run_module`; if the shebang interpreter doesn't exist, fall back to `sys.executable`.

## Verification

- [x] `PYTHONPATH=lib uv run pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -x -v` passes.
