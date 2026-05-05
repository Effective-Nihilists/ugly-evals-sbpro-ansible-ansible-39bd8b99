# Diagnosis: `async_wrapper._run_module` output inconsistency

## Symptom
The `_run_module` function in `lib/ansible/modules/async_wrapper.py` produces JSON output with inconsistent field names, missing fields, and type mismatches across different exit paths (normal completion, OSError/IOError, ValueError/Exception).

## Root Cause
The function has three distinct code paths that construct result dictionaries differently:

### Success path (lines 164-176)
- `result` = module output parsed from JSON (dict from the module)
- `ansible_job_id` is **NOT** added to the result
- `finished: 1` is **NOT** added to the result
- `stderr` only added via `if stderr:` (truthy check — skips empty string)

### OSError/IOError handler (lines 178-188)
- `result` = `{"failed": 1, "cmd": ..., "msg": ..., "outdata": outdata, "stderr": stderr}`
- `failed` is an **integer** (`1`) not boolean
- `ansible_job_id` is added explicitly

### ValueError/Exception handler (lines 190-198)
- `result` = `{"failed": 1, "cmd": ..., "data": outdata, "stderr": stderr, "msg": ...}`  
- Uses `"data"` instead of `"outdata"` — **inconsistent with OSError path**
- `failed` is an **integer** (`1`) not boolean
- `ansible_job_id` is added explicitly

## Key Inconsistencies
1. **Field name**: `"outdata"` (OSError) vs `"data"` (ValueError) — should be `"outdata"` everywhere
2. **Missing fields**: `ansible_job_id` and `finished` missing from success path
3. **`failed` type**: integer `1` in error paths — should be consistent (either int or bool)
4. **`stderr` always needed**: but only set when truthy

## Candidate Fix
In `_run_module`:
1. Set `result['ansible_job_id'] = jid` on success path (after line 176)
2. Set `result['finished'] = 1` on success path  
3. Fix `"data"` → `"outdata"` in ValueError/Exception handler (line 194)
4. Always set `result['stderr']` to `stderr` (remove the `if stderr:` guard, or set it to empty string when no stderr)
5. Keep `failed` as integer `1` for consistency across all error paths and with `main()` which uses `"failed": True` — decide one direction. The test checks `jres.get('rc') == 0` and `jres.get('stderr')` so `failed` is not directly tested, but consistency matters.

## Verification
The test `test_run_module` calls `_run_module(command, jobid, jobpath)` and asserts:
- `jres.get('rc') == 0` 
- `jres.get('stderr') == 'stderr stuff'`

After fix, these assertions must still pass. The added `ansible_job_id` and `finished` fields don't affect these `.get()` calls.
