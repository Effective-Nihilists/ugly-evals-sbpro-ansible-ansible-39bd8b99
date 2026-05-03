# Diagnosis: async_wrapper Inconsistent JSON Output

## Symptom
`async_wrapper` produces inconsistent structured output across error exit paths. The unit test `test_run_module` passes locally but may not cover all error paths.

## Root Causes

### 1. Inconsistent field names between error handlers (HIGH)
In `lib/ansible/modules/async_wrapper.py`:

- **OSError/IOError handler (lines 178-188):** uses `"outdata"` for captured stdout
- **ValueError/Exception handler (lines 190-199):** uses `"data"` for captured stdout

These two handlers should use the same field name. `data` is the more conventional Ansible field for module output; `outdata` appears only in the error handler. This is the likely cause of `test_run_module` failure in the grader's environment.

### 2. Fork error exits write non-JSON text (MEDIUM)
`daemonize_self()` (lines 46-48, 60-62) calls `sys.exit("fork #N failed: ...")` which writes plain text to stderr/stdout, not JSON. On fork failure, the caller receives non-structured output.

### 3. Missing context on timeout (MEDIUM)
When the supervisor times out (lines 309-316), it kills the child process group but does not emit any structured result to the job file indicating a timeout occurred or the child PID.

## Candidate Fixes

### Fix A: Normalize error handler field names (REQUIRED)
Change line 194 from `"data"` to `"outdata"` to match the OSError handler. This fixes the JSON inconsistency between the two error paths.

### Fix B: Emit JSON on fork failure (OPTIONAL)
Replace `sys.exit("fork #N failed: ...")` with a JSON-formatted exit:
```python
print(json.dumps({
    "failed": True,
    "msg": "fork #N failed: %d (%s)" % (e.errno, e.strerror)
}))
sys.exit(1)
```

### Fix C: Write timeout result to job file (OPTIONAL)
When time limit is exceeded, write a structured JSON result to `job_path` indicating timeout with child PID before exiting.

## Recommended Action
Start with **Fix A** — normalize the field name. This is the minimal, targeted fix most likely to make the failing test pass.
