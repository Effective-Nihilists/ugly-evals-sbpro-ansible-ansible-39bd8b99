# Diagnosis: async_wrapper inconsistent error output

## Symptom
The `async_wrapper` module produces inconsistent output formats across different error paths:
- Fork failures in `daemonize_self()` output plain text via `sys.exit("error message")`
- Other error paths (async dir creation, general exceptions) output structured JSON
- This inconsistency makes automated consumption of results unreliable

## Root Cause
The `daemonize_self` function (lines 39-67) was implemented as a generic daemonization utility that uses `sys.exit()` with plain text error messages when `os.fork()` fails. However, in the context of `async_wrapper`, all error paths should output consistent JSON structure for reliable automated processing.

## Candidate Fixes

### Option 1: Modify `daemonize_self` to output JSON
- **Pros**: Direct fix, maintains single responsibility
- **Cons**: `daemonize_self` becomes coupled to async_wrapper's output format

### Option 2: Handle fork errors in main() instead of `daemonize_self`
- **Pros**: Keeps `daemonize_self` generic, centralizes error handling
- **Cons**: Requires restructuring the daemonization logic

### Option 3: Wrap `daemonize_self` calls with exception handling
- **Pros**: Minimal change, preserves existing structure
- **Cons**: Error handling is split between functions

## Chosen Approach
Option 1 is best because:
1. `daemonize_self` is only used within `async_wrapper` 
2. The function already contains async_wrapper-specific logic (syslog calls)
3. Simplest implementation with clearest error handling

## Expected Output Structure
All error paths should output:
```json
{
  "failed": true,
  "msg": "Descriptive error message",
  "exception": "Traceback (when appropriate)"
}
```