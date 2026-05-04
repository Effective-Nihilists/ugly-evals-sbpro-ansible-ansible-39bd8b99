# Diagnosis

## Symptom
Running the full test suite fails during collection with `ModuleNotFoundError: No module named 'ansible.module_utils.six.moves'`. This error occurs for any import that eventually imports `ansible.module_utils.six`.

## Root cause
The bundled `ansible.module_utils.six` package is incomplete. The file `lib/ansible/module_utils/six/__init__.py` is empty, so the `six` compatibility layer and its `moves` submodule are missing. Many modules import from `ansible.module_utils.six` and expect the full six implementation.

## Candidate fixes
- **Add full six implementation**: copy the upstream `six` library into `lib/ansible/module_utils/six/` (including `__init__.py`, `moves/` etc.). This restores the expected symbols and resolves import errors across the codebase.
- **Redirect imports**: modify all imports of `ansible.module_utils.six` to import the system `six` package (`import six`), but this is invasive and may break compatibility with bundled expectations.
- **Provide minimal shim**: implement a minimal subset of six needed for the imports (e.g., define `string_types`, `iteritems`, `PY3`, and a `moves` namespace with required symbols). Simpler but risk missing some uses.

**Trade‑offs**: Full copy ensures compatibility with all existing code and tests, but adds a large third‑party library to the repo. A shim is smaller but may miss edge cases. Redirecting imports is the most invasive and could affect downstream users.

**Recommended fix**: Add the full six library under `lib/ansible/module_utils/six/` (including `moves` submodule) to match the bundled expectations.