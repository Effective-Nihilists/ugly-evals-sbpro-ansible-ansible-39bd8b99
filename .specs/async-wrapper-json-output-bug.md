# async_wrapper JSON output bug

## Repro
Test module prints `print('{"rc": 0}')` → outputs `'{"rc": 0}'` (single-quoted JSON).
`_filter_non_json_lines` only checks `line.startswith('{')` → fails to find JSON → raises `ValueError` → `_run_module` catches it in the `except (ValueError, Exception)` block with `failed: 1`.

## Root Cause
`lib/ansible/module_utils/json_utils.py`'s `_filter_non_json_lines` (copied into `async_wrapper.py:72`) only detects JSON when a line starts with `{`. It doesn't handle quoted JSON like `'{"rc": 0}'`.

## Fix
Update `_filter_non_json_lines` in `lib/ansible/modules/async_wrapper.py` to also check for lines that start with `'` or `"` (indicating quoted JSON), and strip one layer of quotes when computing start/end of JSON.

Check for existing patterns in `lib/ansible/module_utils/json_utils.py` — ticket says to ensure changes propagate there too.