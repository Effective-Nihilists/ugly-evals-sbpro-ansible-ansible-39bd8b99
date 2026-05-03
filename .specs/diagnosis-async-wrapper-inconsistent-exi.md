# Diagnosis: async_wrapper inconsistent exit paths

## Symptom
`async_wrapper` emits non-uniform output across error paths:
- Fork #1 failure: raw string `"fork #1 failed: %d (%s)\n"`
- Fork #2 failure: raw string `"fork #2 failed: %d (%s)\n"`
- Timeout: plain `sys.exit(0)` (no output at all)

Expected: consistent JSON with `failed`, `msg`, `ansible_job_id`, and contextual fields.

## Root Cause
Three error paths in `lib/ansible/modules/async_wrapper.py` use raw strings or bare exit codes instead of structured JSON:
- `daemonize_self()` lines 46-52: fork #1 OSError exits raw string
- `daemonize_self()` lines 64-70: fork #2 OSError exits raw string
- `_run_module()` lines 324-329: timeout exits `sys.exit(0)` with no output

## Candidate Fixes
1. **Change all three to emit `json.dumps({...})` with consistent fields** — done
2. **Add `ansible_job_id` to fork failures** — needed for traceability; fork errors occur before jid is written to job file

## Changes Made (FIX step)
1. Fork #1 OSError → `sys.exit(json.dumps({"failed": True, "msg": "fork #1 failed...", "ansible_job_id": jid}))`
2. Fork #2 OSError → same structure
3. Timeout → `sys.exit(json.dumps({"msg": "timed out waiting for result", "failed": True, "ansible_job_id": jid, "child_pid": sub_pid}))`

## Verification
`pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v` → PASSED