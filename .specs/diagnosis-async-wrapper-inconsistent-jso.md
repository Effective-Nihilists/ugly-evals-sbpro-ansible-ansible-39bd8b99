# Fix Applied: async_wrapper Inconsistent JSON Output

## Changes Made

### 1. Normalized field name in ValueError handler (line 194)
Changed `"data"` → `"outdata"` to match the OSError handler. Both exception paths now use the same field name for stdout content.

### 2. Added `ansible_job_id` to `main()` error handler (line 339)
The top-level exception handler now includes `ansible_job_id` in its JSON output, consistent with all other exit paths.

### 3. Fork failure exit paths emit JSON (lines 46-48, 58-62)
Both `daemonize_self()` fork failure exits now call `sys.exit(json.dumps({...}))` instead of raw strings.

### 4. Timeout exit path emits JSON with child PID (lines 313-316)
The timeout handler now emits structured JSON with `failed`, `msg`, `ansible_job_id`, and `ansible_child_pid` fields before exiting.

## Verification
- `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` → **PASSED**

## Files Modified
- `lib/ansible/modules/async_wrapper.py`
  - Line 46-48: fork #1 failure → JSON
  - Line 58-62: fork #2 failure → JSON
  - Line 194: `"data"` → `"outdata"` in ValueError exception handler
  - Line 313-316: timeout exit → JSON with `ansible_child_pid`
  - Line 339: Added `"ansible_job_id": jid` to main() exception handler JSON output