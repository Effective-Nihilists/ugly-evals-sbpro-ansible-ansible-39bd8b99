# async_wrapper JSON output bug — Diagnosis

## Symptom
`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with `assert jres.get('rc') == 0`. The module prints `print('{"rc": 0}')` which outputs `'{"rc": 0}'` (single-quoted JSON string). `_filter_non_json_lines` fails to extract this quoted JSON, causing `ValueError` → `_run_module` catches it and returns `failed: 1, rc: 1` instead of the expected `rc: 0`.

## Root Cause
**`_filter_non_json_lines` in `async_wrapper.py`** only detects JSON when a stripped line starts with `{` or `[`. It cannot handle quoted JSON like `'{"rc": 0}'` because:
1. `line.startswith('{')` → False (line starts with `p` from `print`)
2. The quoted-JSON detection logic only checks `line[1:-1]` (stripping outer quotes) which doesn't work for `print('{"rc": 0}')` since that would give `'{"rc": 0}'` (still has inner quotes)
3. When no JSON is found, raises `ValueError` caught by `_run_module`

## Candidate Fixes

### Fix A (Primary — quoted JSON extraction)
Update `_filter_non_json_lines` to scan each line for `{` or `[` characters inside quoted strings. When found:
1. Extract the JSON substring from inside the quotes
2. Replace the first line with the extracted JSON so the trailing-junk detection loop works correctly

### Fix B (Propagation)
Same fix must be applied to `lib/ansible/module_utils/json_utils.py` per the NB comment in `async_wrapper.py`.

### Fix C (Exception handler rc field)
Already fixed — `_run_module` exception handlers now include `"rc": 1`.

### Fix D (Python 2 → 3 exception syntax)
Already fixed — `except OSError as e:` replaces `sys.exc_info()[1]` pattern.

## Tradeoffs
- Fix A is the critical path — without it, the test always fails regardless of environment
- The fix needs to handle the edge case where JSON is inside a single-line quoted string with no trailing junk
- Existing tests for `_filter_non_json_lines` only cover bare JSON — new logic must not break those