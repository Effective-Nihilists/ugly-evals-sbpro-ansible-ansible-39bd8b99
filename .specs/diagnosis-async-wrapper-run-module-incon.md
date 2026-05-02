# Diagnosis: async_wrapper `_run_module` inconsistent output

## Symptom
`test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails with `assert None == 0` — the job file result dict has no `rc` key.

## Root Cause
The test creates a temp script with shebang `#!/usr/bin/python` and mocks `_get_interpreter` to return `['/usr/bin/python']`. On systems where `/usr/bin/python` doesn't exist (macOS, some Docker images), `subprocess.Popen` raises `OSError`.

The `OSError` is caught by the `except (OSError, IOError)` handler at line 178, which writes a result dict with `failed: 1` but **no `rc` key**. The test then reads the job file and asserts `jres.get('rc') == 0`, which fails because `rc` is absent.

However, the **real bug per the ticket** is broader: `_run_module` produces inconsistent output across exit paths:
1. **Success path** (line 164): `result = json.loads(filtered_outdata)` — preserves whatever the module returned (e.g., `{'rc': 0}`)
2. **OSError/IOError path** (line 180-188): result has `failed`, `cmd`, `msg`, `outdata`, `stderr`, `ansible_job_id` — but no `rc`
3. **ValueError/Exception path** (line 190-199): result has `failed`, `cmd`, `data`, `stderr`, `msg`, `ansible_job_id` — uses `data` instead of `outdata`, no `rc`

Inconsistencies:
- Field name differs: `outdata` (OSError) vs `data` (ValueError/Exception)
- Neither error path includes `rc`
- Neither error path includes `ansible_job_id` consistently (both do now, but the pattern is ad-hoc)

## Candidate Fixes

### Fix A: Add `rc` to error paths + standardize field names
Add `"rc": 1` to both error handlers. Rename `data` to `outdata` in the ValueError/Exception handler for consistency.

**Tradeoff**: Minimal change, directly addresses the test failure and the inconsistency. Low risk.

### Fix B: Restructure _run_module with a single result construction
Refactor to build result once at the end, merging module output with error context.

**Tradeoff**: Cleaner long-term, but larger change with higher regression risk. Overkill for this bug.

## Recommended Fix: Fix A
1. In the `except (OSError, IOError)` block (line 180-188): add `"rc": 1` to the result dict
2. In the `except (ValueError, Exception)` block (line 190-199): add `"rc": 1` and rename `"data"` to `"outdata"` for consistency

## Verification
Run: `PYTHONPATH=lib:. pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs`
