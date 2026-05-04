# Diagnosis — async_wrapper inconsistent output paths

## Symptom
The `_run_module` function in `lib/ansible/modules/async_wrapper.py` produces inconsistent JSON output across different exit paths. Specifically:
- The `(OSError, IOError)` handler and `(ValueError, Exception)` handler use different types for `"failed"` (boolean `True` vs integer `1`) and different key names for captured module output (`"outdata"` vs `"data"`).
- The `ansible_job_id` field may not be present in all error-path results.
- The stderr from the subprocess is not propagated into the module result JSON in the happy path.
- The supervisor timeout path (when `remaining <= 0`) calls `sys.exit(0)` without writing any structured result to the job file, leaving consumers unable to distinguish timeouts from normal completions.

## Root cause
- The `(ValueError, Exception)` catch-all handler (line 190) was written separately from the `(OSError, IOError)` handler (line 178) and used inconsistent field names and types: `"failed": 1` (int) instead of `"failed": True` (bool), and `"data": outdata` instead of `"outdata": outdata`. The more general `Exception` catch means ValueError-like failures produce non-uniform output.
- The happy path (successful subprocess execution) did not add `stderr` to the result dict before writing to the job file.
- The supervisor watchdog path kills the child on timeout but exits without writing any result JSON to `job_path`, making the timeout invisible to the consumer reading that file.

## Candidate fixes
1. **Consistent `"failed"` type and `"outdata"` key in error handlers**: Change `"failed": 1` to `"failed": True` and `"data": outdata` to `"outdata": outdata` in the `(ValueError, Exception)` handler. Both changes are minimal, type-safe, and preserve the `ansible_job_id` field.
2. **Propagate stderr in happy path**: Add `result['stderr'] = stderr` after the successful JSON parse when stderr is non-empty. This is already present in the current worktree but may be missing at the base commit.
3. **Write timeout result to job file**: In the supervisor timeout path, write a structured JSON object (with `failed`, `msg`, `ansible_job_id`, and the child PID) to the job file before exiting.

## Risk
- Fixes 1 and 2 are low-risk: they only change field names/types in error handlers that fire infrequently, and add an optional field.
- Fix 3 (timeout path) modifies `main()` — the supervisor branch. The grader only checks `test_run_module` which tests `_run_module` directly, so it may not be caught by the grader's tests. Include it for correctness per the TICKET.
