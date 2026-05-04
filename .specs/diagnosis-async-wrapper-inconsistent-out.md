# Diagnosis: async_wrapper inconsistent output

## Symptom
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes in the current environment, but the ticket indicates it should be failing after the fix is applied. The test only covers the `_run_module` happy path, not the wrapper's various exit paths.

## Root Cause
The `async_wrapper` module has inconsistent JSON output across different exit paths:

1. **Fork #1 failure** (lines 46-52): Already returns proper JSON with `failed` and `msg` fields - GOOD
2. **Fork #2 failure** (lines 60-62): Returns plain text `"fork #2 failed: %d (%s)\n"` via `sys.exit()` - NOT JSON
3. **Timeout**: Need to find the exact line - likely missing JSON output
4. **Async directory creation failure**: Need to verify

## Specific Issues Found
- Fork #2 error at line 62: Uses `sys.exit("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))` which is plain text, not JSON

## Candidate Fixes
1. **Fork #2 failure**: Replace `sys.exit("fork #2 failed: ...")` with JSON output matching the fork #1 pattern:
   ```python
   print(json.dumps({
       "failed": True,
       "msg": "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
   }))
   sys.exit(1)
   ```
2. **Timeout path**: Add JSON output before exit that includes the child PID for context
3. Ensure all exit paths emit exactly one JSON object with consistent fields

## Tradeoffs
- Changing exit paths could affect existing playbooks that parse the output
- Need to ensure backward compatibility for normal completion path
- The fix should be minimal and focused on the inconsistent paths