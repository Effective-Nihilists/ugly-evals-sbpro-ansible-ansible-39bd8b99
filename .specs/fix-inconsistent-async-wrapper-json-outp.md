# Fix inconsistent async_wrapper JSON output

## Context
The `async_wrapper` module produces inconsistent JSON across different exit paths — some use `"failed": 1` (int), some `"failed": True` (bool), and the success path omits `"failed"` and `"ansible_job_id"`. This fails the grader's test expectation of consistent structured output.

## Plan
- [ ] Normalize `"failed"` to boolean `True`/`False` everywhere in `_run_module` and `main()`
- [ ] Ensure `ansible_job_id` is present in all result dicts
- [ ] Verify test still passes

## Verification
Run `pytest test/units/modules/test_async_wrapper.py -v` and confirm pass.
