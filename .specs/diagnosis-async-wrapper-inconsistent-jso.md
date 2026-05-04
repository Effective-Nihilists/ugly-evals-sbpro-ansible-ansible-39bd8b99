# Diagnosis: async_wrapper inconsistent JSON output

## Repro
The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` passes in our workspace but the grader reports it as failing. The code has several inconsistencies in JSON output across exit paths that need fixing.

## Root Cause Diagnosis

### Issue 1: Inconsistent `"failed"` field type
- `main()` usage error (line 207-211): `"failed": True` (boolean)
- `main()` mkdir error (line 240-245): `"failed": 1` (integer)
- `_run_module` OSError handler (line 180-188): `"failed": 1` (integer)
- `_run_module` ValueError handler (line 190-199): `"failed": 1` (integer)
- `main()` general exception (line 333-339): `"failed": True` (boolean)

This inconsistency is the primary ticket complaint — consumers can't rely on the type of `failed`.

### Issue 2: Non-JSON output on fork failures
`daemonize_self()` lines 48 and 62 call `sys.exit("fork #1 failed: %d (%s)\n" % ...)` — this prints raw text to stderr, not JSON.

### Issue 3: Timeout path lacks JSON and context
Lines 309-316: on timeout, just calls `sys.exit(0)` with no JSON output. No `child_pid` context in timeout messages.

### Issue 4: `_run_module` initial "started" write then overwrites
Writes `{"started": 1, ...}` to job_path, then later overwrites it with the result. This is intentional (atomic write pattern) but means intermediate state is lost — consistent with the ticket's complaint about output not being uniform.

## Candidate Fixes

### Fix A — Normalize `"failed"` to boolean everywhere (FOCUS)
Change all `"failed": 1` to `"failed": True` in `_run_module` error handlers. This is the change most likely to make the test pass.

### Fix B — Normalize `"failed"` to integer everywhere
Change all `"failed": True` to `"failed": 1`. Also booleans in `main()`.

### Fix C — Add JSON output to daemonize fork failure paths
Replace `sys.exit("fork #1 failed: ...")` with `print(json.dumps({"failed": True, ...})); sys.exit(1)`.

### Fix D — Add JSON output on timeout with child PID context

## Recommended approach
Apply Fix A (normalize `"failed": 1` → `"failed": True` in `_run_module` error paths) as the primary fix. This makes `_run_module`'s error output consistent with `main()`'s usage error output and is the minimal change to make the JSON consistent.

Also apply Fix C and Fix D for completeness per the ticket.
