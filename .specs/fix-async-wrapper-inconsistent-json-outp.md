# Fix async_wrapper inconsistent JSON output

## Context

The `async_wrapper` module in lib/ansible/modules/async_wrapper.py produces inconsistent/incomplete JSON output across different exit paths (fork failures, timeouts, async dir creation failures). The test `test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` is failing.

## Plan

- [ ] Find and read the async_wrapper source code
- [ ] Read the failing test to understand what it expects
- [ ] Run the test to reproduce the failure
- [ ] Diagnose the specific issues
- [ ] Fix the source code (not the test)
- [ ] Verify the test passes

## Verification

```bash
pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module -v 2>&1
```
