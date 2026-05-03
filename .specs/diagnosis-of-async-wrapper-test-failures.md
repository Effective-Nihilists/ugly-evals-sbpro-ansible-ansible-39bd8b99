# Diagnosis of async_wrapper test failures

## Symptom
- Running the full test suite fails during import with `ModuleNotFoundError: No module named 'ansible.module_utils.six.moves'`.
- The specific unit test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` cannot be executed because the import chain aborts early.
- The async_wrapper module itself can be imported in isolation, but the surrounding codebase relies heavily on the bundled `six` compatibility shim.

## Root Cause
- The repository is missing the `ansible/module_utils/six` package that provides the `six` compatibility layer and its `moves` submodule.
- Many modules import symbols such as `configparser`, `urllib.error`, `shlex_quote`, `zip`, `reduce`, `map`, etc., from `ansible.module_utils.six.moves`.
- Without this shim, Python raises `ModuleNotFoundError`, halting test collection.

## Candidate Fixes
1. **Add a full stub implementation of `ansible/module_utils/six`**
   - Create `lib/ansible/module_utils/six/__init__.py` with minimal definitions for the symbols used across the codebase.
   - Provide a `moves` package containing submodules (`urllib`, `shlex`, `zip`, etc.) that expose the required attributes.
   - **Trade‑off:** Larger change but restores compatibility for all imports; low risk as it mirrors Ansible's bundled six library.
2. **Vendor the original Ansible `six` module**
   - Copy the upstream `six` implementation from Ansible's source into `lib/ansible/module_utils/six`.
   - **Trade‑off:** Guarantees feature‑complete compatibility; may introduce unnecessary code size.
3. **Patch imports to use the system `six` package**
   - Replace `from ansible.module_utils.six import ...` with `import six` where possible.
   - **Trade‑off:** Invasive, many files to modify; risk of missing edge cases; not preferred for minimal fix.

**Recommended approach:** Implement a minimal stub (option 1) that defines only the symbols required by the test suite, ensuring imports succeed without extensive code changes.

---
*This spec records the diagnosis; the next FIX step will implement the chosen solution.*