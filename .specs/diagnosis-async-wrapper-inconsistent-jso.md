# Fix Applied: async_wrapper Inconsistent JSON Output

## Changes Made

### 1. Normalized field name in ValueError handler (line 194)
Changed `"data"` → `"outdata"` to match the OSError handler. Both exception paths now use the same field name for stdout content.

### 2. Added `ansible_job_id` to `main()` error handler (line 339)
The top-level exception handler now includes `ansible_job_id` in its JSON output, consistent with all other exit paths.

## Verification
- `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` → **PASSED**

## Files Modified
- `lib/ansible/modules/async_wrapper.py`
  - Line 194: `"data"` → `"outdata"` in ValueError exception handler
  - Line 339: Added `"ansible_job_id": jid` to main() exception handler JSON output