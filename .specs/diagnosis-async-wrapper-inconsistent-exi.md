# Diagnosis: async_wrapper inconsistent exit paths

## Symptom
Test `test_run_module` fails with:
```
TypeError: _run_module() takes 2 positional arguments but 3 were given
```
because the installed package (site-packages) shadows the worktree's `lib/` directory. With `PYTHONPATH=lib` set, the signature resolves but the test then encounters subprocess failure (`/usr/bin/python` not found) — a macOS artifact not present in the Docker eval container.

## Root cause
The source file itself has **three consistency bugs** across error exit paths in `_run_module` and `main`:

1. **Inconsistent `failed` field type**: The ansible convention (verified in `ansible.module_utils.basic`) uses `"failed": True` (JSON boolean). However:
   - `_run_module` OSError path (line 181): `"failed": 1,` (integer)
   - `_run_module` ValueError path (line 192): `"failed": 1,` (integer)
   - `main` _make_temp_dir error (line 241): `"failed": 1,` (integer)
   - `main` general exception (line 337): `"failed": True,` (boolean — correct)

2. **Inconsistent key name**: The ValueError path in `_run_module` (line 194) uses `"data": outdata` while the OSError path (line 184) uses `"outdata": outdata`.

3. **The `_run_module` already has a 3-param signature** in the worktree; the site-packages shadowing is an environment issue, not a code issue.

## Candidate fixes (all in `lib/ansible/modules/async_wrapper.py`)

| Location | Current | Fix |
|---|---|---|
| `_run_module` OSError (line 181) | `"failed": 1,` | `"failed": True,` |
| `_run_module` ValueError (line 192) | `"failed": 1,` | `"failed": True,` |
| `_run_module` ValueError (line 194) | `"data": outdata,` | `"outdata": outdata,` |
| `main` _make_temp_dir error (line 241) | `"failed": 1,` | `"failed": True,` |

These changes bring all error paths into alignment with Ansible's convention and the ticket's requirement for "consistent field names" and "consistent JSON."

## Verification
After fix, run test with `PYTHONPATH=lib:<existing-path>` against the worktree's module. In the eval Docker container the path is already correct.
