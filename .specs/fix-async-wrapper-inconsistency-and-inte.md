# Fix: async_wrapper inconsistency and interpreter fallback

## Context

The `async_wrapper` module in ansible produces inconsistent output across exit paths (fork errors, timeouts, directory errors). Additionally, `_run_module` fails when the shebang interpreter path (e.g. `/usr/bin/python`) doesn't exist on the system — the mock in `test_run_module` returns `['/usr/bin/python']` but some Docker environments lack that path, causing `subprocess.Popen` to raise `OSError`.

## Plan

- [x] **Reproduce**: Confirm the test failure behavior by running the test.
- [ ] **Standardize `"data"` → `"outdata"`**: In the `except (ValueError, Exception):` handler of `_run_module`, change the output key from `"data"` to `"outdata"` for consistency with the `OSError` handler.
- [ ] **Add interpreter existence check in `_run_module`**: After `_get_interpreter` returns a path, check `os.path.exists(interpreter[0])`. If it doesn't exist, fall back to `sys.executable`.
- [ ] **Standardize `"failed"` field**: In `main()`, change `"failed": 1` (int) to `"failed": True` (bool) for consistency with the `except Exception:` handler in main.

## Verification

- Run `python -m pytest test/units/modules/test_async_wrapper.py -xvs` and confirm it passes.
