# async_wrapper JSON output bug — Diagnosis

## Symptom
`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with `assert None == 0`. The job result dict is missing the `rc` field when the subprocess fails (e.g., `/usr/bin/python` not found).

## Root Cause (confirmed)
**Python 2 → Python 3 exception syntax incompatibility** in `lib/ansible/modules/async_wrapper.py`, lines 46 and 60:
```python
except OSError:
    e = sys.exc_info()[1]  # Python 2 style — returns None in Python 3!
```
In Python 3, `sys.exc_info()[1]` returns `None` when used with `except OSError:` (no `as e`). This means:
1. `msg: None` — unhelpful error message
2. `outdata` is **unbound** (error occurs during `subprocess.Popen` before assignment) — referencing it causes `NameError`
3. Result dict is missing `rc`

**Secondary issue**: `_filter_non_json_lines` in `async_wrapper.py` only detects JSON when a stripped line starts with `{` or `[`. It fails to parse quoted JSON like `print('{"rc": 0}')` which outputs `'{"rc": 0}'`. This was already partially fixed but the quoted-JSON detection logic has edge cases.

## Candidate Fixes

### Fix A (Primary — Exception handler syntax)
Change both OSError handlers to Python 3 style:
```python
except OSError as e:
```
This ensures `e` is bound correctly, `msg` contains the error text, and avoids `NameError` on unbound `outdata`.

### Fix B (Secondary — quoted JSON detection)
The `_filter_non_json_lines` in `async_wrapper.py` needs to detect quoted JSON lines (starting with `'` or `"`). The current detection logic fails when the entire output is a single quoted JSON string like `'{"rc": 0}'` because the stripped line still starts with `p` (the print statement), not the quote. Need to scan for the first `{` character anywhere within each line.

### Fix C (json_utils.py propagation)
Per the NB comment in `async_wrapper.py`, changes to `_filter_non_json_lines` should propagate to `lib/ansible/module_utils/json_utils.py`. The quoted-JSON handling should be added there too.

## Tradeoffs
- Fix A is minimal and safe — changes only the exception syntax
- Fix B requires more complex logic (find `{` anywhere in line, not just at position 0)
- Fix C ensures consistency across the codebase as documented