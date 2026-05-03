# Diagnosis Spec

## Symptom
- Test suite fails during collection with `ModuleNotFoundError: No module named 'ansible.module_utils.six.moves'`.
- The async_wrapper unit test passes when run in isolation, but the overall failure masks the async_wrapper inconsistency described in the ticket.

## Root Cause
- The vendored `six` compatibility package is incomplete: the directory `lib/ansible/module_utils/six/moves/` and its `__init__.py` are missing. Many modules import `ansible.module_utils.six.moves` (e.g., for `urllib`, `zip`, `configparser`). The missing file triggers import errors across the codebase, preventing test collection and hiding the async_wrapper bug.

## Candidate Fixes
- **Add missing `six.moves` package**: create `lib/ansible/module_utils/six/moves/__init__.py` that re-exports the standard `six.moves` implementation (e.g., `from six.moves import *`). This restores compatibility for all imports.
- **Adjust imports to use the bundled `six` directly**: replace `ansible.module_utils.six.moves` imports with `six.moves` where feasible, reducing reliance on the vendored shim.
- **Fallback to system `six`**: modify `lib/ansible/module_utils/six/__init__.py` to import the external `six` package if present, ensuring `moves` submodule is available.

## Trade‑offs
- Adding the missing module is the minimal invasive change and restores existing import expectations without touching many files.
- Refactoring imports would be more extensive and risk missing edge cases.
- Relying on system `six` could introduce version mismatches in environments where the bundled version is required.

## Next Steps (FIX)
- Implement the missing `six.moves` package as described.
- Run the full test suite to verify that import errors are resolved and then address the async_wrapper inconsistency if still failing.
