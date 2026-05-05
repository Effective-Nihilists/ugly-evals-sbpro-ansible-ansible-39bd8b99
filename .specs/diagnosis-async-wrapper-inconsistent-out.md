# Context
The `async_wrapper` module in Ansible has inconsistent JSON output across different exit paths, making it unreliable for automated consumption of results.

# Repro
Run test: `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module`

# Diagnosis

## Root Cause Analysis

The `async_wrapper` module has inconsistent JSON output across different exit paths:

1. **Fork failures don't produce JSON output** (lines 48, 62 in async_wrapper.py):
   - In `daemonize_self()`, fork failures call `sys.exit()` with string messages
   - Expected: JSON with {"failed": 1, "msg": "...", "ansible_job_id": jid}
   - Actual: Plain text error messages

2. **Timeout results don't include child PID** (lines 310-316):
   - When killing timed-out processes, the result doesn't include child PID
   - Expected: {"failed": 1, "msg": "timeout", "ansible_job_id": jid, "child_pid": sub_pid}
   - Actual: No child PID in timeout results

3. **Async directory creation errors have non-standard messages** (lines 240-245):
   - Error messages are inconsistent with other error paths
   - Expected: Standardized JSON with consistent field names
   - Actual: Non-standard error format

4. **Exception handler in main() doesn't include ansible_job_id** (lines 336-340):
   - The exception handler doesn't include job ID in error response
   - Expected: {"failed": True, "msg": "...", "ansible_job_id": jid}
   - Actual: Missing ansible_job_id field

## Candidate Fixes

1. **Fix fork failures**: Replace `sys.exit(string)` with JSON output
2. **Add child PID to timeout results**: Include sub_pid in timeout JSON
3. **Standardize error messages**: Use consistent field names across all exit paths
4. **Add ansible_job_id to all error responses**: Ensure job ID is included in all error JSON

## Trade-offs
- Changes to error output may affect existing playbooks that parse error messages
- Adding child PID increases output size slightly but provides valuable debugging info
- Standardizing messages improves reliability but requires careful testing of all exit paths