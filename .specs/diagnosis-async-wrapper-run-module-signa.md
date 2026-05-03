# Diagnosis: `_run_module` has no return statement

## Symptom
```
assert None == 0
```
Test calls `async_wrapper._run_module(command, jobid, jobpath)` and the result is `None`.

## Confirmed Facts
1. Source defines `_run_module(wrapped_cmd, jid, job_path)` — **3 parameters, matching call**
2. Bytecode `co_argcount = 3`, function called with 3 args — **no TypeError**
3. **`_run_module` has NO return statements** — only writes to job file via `jobfile.write(json.dumps(result))` then falls through to `return None`
4. Function correctly creates the job file with JSON result, but doesn't return it to caller
5. Ticket description: "inconsistent output" — missing structured return values

## Root Cause
`_run_module` at line 129 builds a `result` dict, writes it to the job file, but never returns it. Every code path (normal completion, OSError, ValueError) falls through to `None`.

## Fix
Add `return result` at the end of each code path in `_run_module`, OR a single `return result` after all try/except blocks close.

Candidate fix in `lib/ansible/modules/async_wrapper.py`:
- After line 176 (normal completion `jobfile.write`), add `return result`
- After line 188 (OSError/IOError), add `return result`
- After line 199 (ValueError/Exception), add `return result`

OR simpler: move `return result` to after the `except` blocks close (after line 201).

## Files to Edit
- `lib/ansible/modules/async_wrapper.py` — add `return result` statements in `_run_module`