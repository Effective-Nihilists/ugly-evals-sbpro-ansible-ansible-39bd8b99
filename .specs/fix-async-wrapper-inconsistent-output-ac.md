# Fix async_wrapper inconsistent output across exit paths

## Context
The `async_wrapper` module produces inconsistent JSON across exit paths (fork errors, timeouts, missing async directory, normal completion). Field names differ (`outdata` vs `data`), `failed` mixes `1` (int) and `True` (bool), and some paths omit fields like `ansible_job_id` or `stderr`.

## Plan
- [ ] Read the test and source to understand current behavior
- [ ] Fix `_run_module` to produce consistent JSON across all exit paths
- [ ] Verify the test passes

## Verification
`cd /private/var/.../worktree && uv run pytest test/units/modules/test_async_wrapper.py -v`
