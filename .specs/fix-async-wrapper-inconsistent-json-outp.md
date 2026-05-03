## Diagnosis

### Symptom

`async_wrapper` produces inconsistent or incomplete JSON output across different exit paths (normal completion, OSError/IOError, ValueError, async dir creation failure, general exception, timeout). This makes automated consumption of results unreliable.

### Root cause

1. **`failed` field uses inconsistent types** — Three error paths use `"failed": 1` (integer):
   - `_run_module` OSError/IOError handler (line ~180)
   - `_run_module` ValueError/Exception handler (line ~192)
   - `main()` async dir creation failure (line ~240)
   
   But the general exception handler in `main()` (line ~336) uses `"failed": True` (boolean). Ansible convention expects `failed` to be a boolean True/False, not integer 1/0.

2. **Inconsistent field name `data` vs `outdata`** — The ValueError/Exception handler in `_run_module` (line ~194) writes `"data": outdata` while the OSError/IOError handler (line ~184) writes `"outdata": outdata`. These should use the same field name so consumers can rely on a known key.

3. **Timeout path produces no structured output** — When the watcher process detects timeout and kills the child (lines ~309-316), it calls `sys.exit(0)` without writing any result to the job file. The job file retains the initial `{"started": 1, "finished": 0}` status permanently — the caller sees "not finished" forever with no timeout signal.

### Candidate fixes

1. **Change all `"failed": 1` to `"failed": True`** — Makes the type consistent across all error paths using boolean.

2. **Change `"data"` to `"outdata"`** in the ValueError/Exception handler — Makes the field name consistent with the OSError/IOError handler.

3. **Write a timeout result to the job file** — Before the watcher exits on timeout, write `{"failed": True, "msg": "timed out", "ansible_job_id": jid, "finished": 1}` to the job_path so callers see a definite timeout result instead of a perpetually-"started" status.
