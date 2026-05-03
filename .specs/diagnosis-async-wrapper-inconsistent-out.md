# Fix — async_wrapper consistent JSON output

## Changes made to `lib/ansible/modules/async_wrapper.py`

### Problem
The `_run_module` function built result dicts differently across three exit paths (success, OSError/IOError, ValueError/Exception), causing inconsistent field types and names.

### Fix (3 edits in `_run_module`)
1. **Success path**: Added `result['ansible_job_id'] = jid` before writing the result file (was missing)
2. **OSError/IOError path**: Changed `"failed": 1` → `"failed": True` for bool consistency; added `result['ansible_job_id'] = jid`  
3. **ValueError/Exception path**: Changed `"failed": 1` → `"failed": True`; changed `"data": outdata` → `"outdata": outdata`; added `result['ansible_job_id'] = jid`

All three paths now emit consistent JSON with field `"failed"` as bool, use `"outdata"` as the output data key, and include `ansible_job_id`.

### Verification
Simulated with `python3`: subprocess runs, stdout `{'rc': 0}` is parsed, stderr captured, `ansible_job_id` set. `rc == 0` and `stderr == 'stderr stuff'` both pass.
