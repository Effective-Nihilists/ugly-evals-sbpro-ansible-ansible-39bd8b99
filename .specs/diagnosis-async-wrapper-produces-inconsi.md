# Diagnosis: async_wrapper produces inconsistent information across exit paths

## Symptom
The `async_wrapper` module returns inconsistent or incomplete information when processes terminate, especially under failure conditions. Output isn't uniform across normal completion, fork failures, timeouts, or errors creating the async job directory.

## Root Cause
After analyzing the code in `lib/ansible/modules/async_wrapper.py`, I identified several issues:

1. **File handling bug in `_run_module` function**: 
   - Lines 132-135: Creates `tmp_job_path`, writes initial status, closes, then renames to `job_path`
   - Line 136: Tries to open `tmp_job_path` again (which no longer exists after rename)
   - This causes an IOError when attempting to write final results, leading to inconsistent error handling

2. **Inconsistent JSON output structure across exit paths**:
   - Normal supervisor return (lines 275-276): `{"started": 1, "finished": 0, "ansible_job_id": jid, "results_file": job_path, "_ansible_suppress_tmpdir_delete": not preserve_tmp}`
   - Async directory creation failure (lines 240-244): `{"failed": 1, "msg": "...", "exception": "..."}`
   - Fork/exception in main (lines 336-339): `{"failed": True, "msg": "FATAL ERROR: ..."}`
   - Module execution errors in `_run_module` (lines 180-188): `{"failed": 1, "cmd": "...", "msg": "...", "outdata": "...", "stderr": "...", "ansible_job_id": jid}`
   - JSON parsing errors in `_run_module` (lines 191-199): `{"failed": 1, "cmd": "...", "data": "...", "stderr": "...", "msg": "..."}`

3. **Inconsistent field naming and types**:
   - Some paths use `"failed": 1`, others use `"failed": True`
   - Not all error paths include `ansible_job_id`
   - Some include exception traces, others don't
   - Normal path uses `started`/`finished` flags, error paths don't

## Candidate Fixes

### Option 1: Fix file handling and standardize error output
- Fix the `_run_module` file handling bug by properly managing temporary files
- Create a standardized error response function that ensures consistent field names and structure
- Ensure all exit paths include `ansible_job_id` when available
- Use consistent boolean values (`true`/`false` instead of `1`/`True`)

**Tradeoffs**: Requires changes to multiple code paths but provides the most consistent and reliable output.

### Option 2: Minimal fix for file handling only
- Only fix the `_run_module` file handling bug
- Leave existing error output structures as-is

**Tradeoffs**: Addresses the immediate file handling issue but doesn't solve the inconsistency problem described in the ticket.

### Option 3: Comprehensive refactor
- Refactor the entire async_wrapper to use a unified response structure
- Implement proper error handling with consistent field names
- Add proper logging and debugging information

**Tradeoffs**: Most comprehensive solution but highest risk of introducing regressions.

## Recommended Approach
Option 1 is recommended as it addresses both the immediate file handling bug and the core inconsistency issue described in the ticket, while maintaining backward compatibility with existing field names where possible.