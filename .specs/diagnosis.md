# Diagnosis

**Symptom**: Inconsistent JSON output from `async_wrapper` across different execution paths. Some paths omit fields such as `stderr`, `rc`, or `warnings`, leading to test failures that expect a uniform structure.

**Root Cause**: The `_run_module` function builds the result dictionary differently depending on the exception caught:
- In the `OSError/IOError` block it populates `failed`, `cmd`, `msg`, `outdata`, `stderr`, and `ansible_job_id` but omits `rc` and may omit `warnings`.
- In the generic `Exception` block it populates `failed`, `cmd`, `data`, `stderr`, `msg`, and `ansible_job_id` but also omits `rc` and `warnings`.
- When the module runs successfully, `result` comes from parsed JSON and only includes fields present in the module output; `stderr` is added only if present.

This leads to callers receiving result objects with varying keys, breaking expectations for a consistent schema.

**Candidate Fixes**:
1. **Normalize result fields**: After each branch, ensure the result dictionary contains the keys `rc`, `stderr`, `warnings`, and `ansible_job_id` (with sensible defaults, e.g., `rc: 0` for success, empty string for `stderr`, empty list for `warnings`).
   - *Trade‑off*: Slightly larger JSON payload but guarantees schema stability.
2. **Wrap result construction in a helper** that merges the parsed JSON with a default template, reducing duplication.
   - *Trade‑off*: Introduces an extra function but improves maintainability.
3. **Add explicit handling for missing `rc`** in the success path by defaulting to `0` if not provided by the module.
   - *Trade‑off*: Minimal change, directly addresses the most common missing field.

The preferred approach is to implement fix #1 (field normalization) combined with #3 (default `rc`). This provides immediate consistency with minimal code impact.

**Next Step**: Implement the normalization logic in `_run_module` before writing the result to the job file.
