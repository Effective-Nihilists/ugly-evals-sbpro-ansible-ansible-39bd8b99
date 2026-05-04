# Fix async_wrapper inconsistent output across exit paths

## Context

The `async_wrapper` module produces inconsistent or incomplete JSON output across different exit paths:
1. **Timeout**: supervisor kills child process and exits without writing any result to the job file
2. **Fork failure**: uses `"failed": True` instead of `"failed": 1`, missing `ansible_job_id`
3. **Async directory creation failure**: missing `ansible_job_id`
4. **`_run_module` success path**: missing `ansible_job_id` in result (present in error paths)
5. **`_run_module` error paths**: inconsistent field names (`data` vs `outdata`)

## Plan

- [ ] Fix `_run_module` success path: add `ansible_job_id` to result, add `finished: 1`
- [ ] Fix `_run_module` ValueError/Exception path: use `outdata` instead of `data` for consistency
- [ ] Fix `main()` timeout path: write JSON result to job file with timeout context (child_pid, ansible_job_id)
- [ ] Fix `main()` fork error path: use `"failed": 1` consistently, add `ansible_job_id`
- [ ] Fix `main()` directory creation error path: add `ansible_job_id`
- [ ] Run existing test to confirm no regression

## Verification

- `pytest test/units/modules/test_async_wrapper.py -v` passes
- All exit paths produce consistent JSON with `ansible_job_id`, `failed`, `msg` fields
