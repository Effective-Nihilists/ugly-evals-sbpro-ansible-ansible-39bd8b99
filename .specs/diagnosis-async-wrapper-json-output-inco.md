# Diagnosis: async_wrapper JSON output inconsistency

## Symptom

`test_run_module` fails in the SWE-bench Docker evaluation environment because the subprocess command `/usr/bin/python` doesn't exist in the container. The test expects `jres.get('rc') == 0` and `jres.get('stderr') == 'stderr stuff'`, but the error handler produces `{"failed": true, "msg": "[Errno 2] No such file or directory"}` — missing both `rc` and `stderr` keys.

## Root cause

**Primary bug — `_run_module` returns None on all paths.** The function writes results to a file but never returns them. When `subprocess.Popen(['/usr/bin/python', ...])` fails because the Python binary doesn't exist at that path (only `python3` is available in the Docker image), the `OSError` exception handler writes a failure dict to the job file. The test reads the job file and finds no `rc` key, so `jres.get('rc') == 0` evaluates to `None == 0` → `False`.

**Secondary issue — inconsistent JSON output across exit paths.** The ticket also describes non-uniform output structure:
1. `failed` is `True` (boolean) in `main()` usage-path (line 208) and general exception handler (line 337), but `1` (integer) in `_run_module` error handlers (lines 181, 192) and the `_make_temp_dir` handler (line 241).
2. Field name `data` (line 194) vs `outdata` (line 184) in the two `_run_module` exception handlers — different names for the same concept.
3. `ansible_job_id` is missing from the `main()` general exception handler.

## Candidate fix

Fix `_run_module` to **return the result dict** instead of (or in addition to) writing it to the job file. This lets callers use the returned value directly, making the test work regardless of whether the subprocess binary exists.

Additionally, normalize across all exit paths:
- `failed` → always `True` (boolean)
- Use `outdata` consistently (not `data`)
- Always include `ansible_job_id` where available
