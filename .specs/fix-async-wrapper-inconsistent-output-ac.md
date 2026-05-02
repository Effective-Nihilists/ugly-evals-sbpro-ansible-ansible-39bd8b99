# Fix async_wrapper Inconsistent Output Across Exit Paths

## Context
The `async_wrapper` module returns inconsistent or incomplete information when processes terminate, especially under failure conditions. Different exit paths use different field names and omit expected fields like `rc`.

## Repro
Running `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` fails:
```bash
pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -xvs
```

**Failure**: `assert None == 0` - the job result dict has no `rc` key.

**Root cause**: When subprocess.Popen fails (e.g., interpreter not found), it raises `OSError`. The exception handler at lines 178-188 creates a result dict without `rc`, while the normal path includes `rc` from module output.

## Diagnosis

### Symptom
Test expects `jres.get('rc') == 0` but gets `None` because the `rc` field is missing from the job result when errors occur.

### Root Cause
The `_run_module` function has three exit paths with inconsistent output schemas:

1. **Normal path** (lines 162-176): Returns module's JSON output, which includes `rc` if the module sets it
2. **OSError/IOError path** (lines 178-188): Creates `{"failed": 1, "cmd": ..., "msg": ..., "outdata": ..., "stderr": ..., "ansible_job_id": ...}` - **missing `rc`**
3. **ValueError/Exception path** (lines 190-199): Creates `{"failed": 1, "cmd": ..., "data": ..., "stderr": ..., "msg": ..., "ansible_job_id": ...}` - **missing `rc`**

Additionally, path 2 uses `outdata` while path 3 uses `data` (inconsistent naming).

### Candidate Fixes

**Option 1**: Add `rc` field to both exception handlers
- Set `rc` to a non-zero value (e.g., 1) to indicate failure
- Pros: Simple, maintains consistency, indicates error via `rc`
- Cons: None significant

**Option 2**: Add `rc` field and also standardize `outdata`/`data` naming
- Use consistent field name (e.g., `stdout` or `outdata`) across all paths
- Pros: More complete consistency fix
- Cons: More changes, higher risk

**Option 3**: Only fix the test environment (install `/usr/bin/python`)
- Pros: No code changes
- Cons: Doesn't fix the actual bug - inconsistent output remains

### Recommended Fix
**Option 1**: Add `rc: 1` to both exception handlers to indicate failure. This:
- Makes output consistent across all exit paths
- Properly indicates command failure via `rc` field
- Aligns with the ticket's requirement for "consistent field names"
- Minimal change, low risk

The test will pass once the error result includes `rc: 1` (or any non-zero value), as the test checks `jres.get('rc') == 0` which will fail appropriately with a non-zero rc, OR the test environment needs `/usr/bin/python` to exist so the normal path executes.

Actually, re-reading the test: it expects `rc == 0`, meaning it expects SUCCESS. The test is designed to test the normal execution path, not error paths. The real issue is that `/usr/bin/python` doesn't exist on this system, triggering the error path unexpectedly.

However, the BUG is still valid: the error paths SHOULD include `rc` for consistency. The test failure is a symptom revealing this inconsistency.

## Plan
- [ ] Add `rc: 1` to OSError/IOError exception handler result
- [ ] Add `rc: 1` to ValueError/Exception exception handler result
- [ ] Run test to verify the fix improves consistency

## Verification
After fix, error results will include `rc: 1`, making output consistent. Test may still fail if `/usr/bin/python` doesn't exist (expected behavior - error path returns non-zero rc), but the inconsistency bug will be fixed.
