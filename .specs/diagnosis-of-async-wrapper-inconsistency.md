# Diagnosis of async_wrapper inconsistency

## Symptom
- Unit test `test_async_wrapper.py::TestAsyncWrapper::test_run_module` expects the async_wrapper module to always emit a well‑formed JSON result file.
- In the current environment the test suite fails during import because `ansible.module_utils.six.moves` is missing, and the async_wrapper code contains logic that can emit non‑JSON output on error paths (fork failure, JSON filtering).

## Root Cause
1. **Missing bundled `six.moves` shim** – many Ansible modules import `ansible.module_utils.six.moves`. The shim is not present in the test environment, causing import errors before any async_wrapper logic runs.
2. **`_filter_non_json_lines` strictness** – this helper raises `ValueError` when no leading `{` is found, discarding any output that is not pure JSON. If the wrapped module prints warnings or stray text, the async_wrapper will fail to produce JSON.
3. **Fork‑failure exit path** – on a fork error the code calls `sys.exit("fork #1 failed…")`, which writes a plain string and exits without JSON, violating the contract of always returning a JSON object.

## Candidate Fixes (trade‑offs)
- **Add missing `six.moves` shim** – ship the bundled `six` package under `ansible/module_utils/six` or adjust imports to fallback to the standard library `six` if available. This resolves the import cascade for the whole test suite and is low‑risk.
- **Relax JSON filtering** – modify `_filter_non_json_lines` to return the original output when no JSON start is found, or to extract the first JSON object using a regex instead of raising. This makes async_wrapper tolerant of harmless warnings but may hide genuine output errors.
- **Ensure JSON on fork failure** – replace the `sys.exit` path with a `json.dumps({"failed":1, "msg": "fork #1 failed", "ansible_job_id": jid})` write to the result file before exiting. This guarantees a consistent JSON shape even on fatal errors.
- **Combine approaches** – implement the shim and adjust both the filter and fork‑failure handling for full consistency. Slightly more code change but provides a robust solution.

**Recommendation**: Prioritize adding the missing `six.moves` shim to unblock imports, then adjust the fork‑failure path to emit JSON. The filter change can be deferred unless tests reveal warning‑related failures.
