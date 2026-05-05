# Fix inconsistent output in async_wrapper.py

## Context
The `async_wrapper` module produces inconsistent JSON output across different exit paths:
- Mixed `"failed": 1` (int) and `"failed": True` (bool)
- Mixed `"data"` and `"outdata"` field names in error handlers
- Missing structured output on timeout (just `sys.exit(0)`)

## Plan
- [ ] Fix `_run_module` OSError/IOError handler: `"failed": 1` → `"failed": True`
- [ ] Fix `_run_module` ValueError/Exception handler: `"failed": 1` → `"failed": True` and `"data"` → `"outdata"`
- [ ] Fix `main()` `_make_temp_dir` failure: `"failed": 1` → `"failed": True`

## Verification
- Run `pytest test/units/modules/test_async_wrapper.py::TestAsyncWrapper::test_run_module` — must pass
