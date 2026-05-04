# Shim for ansible.module_utils.six.moves
# Provide the standard six.moves submodule by delegating to the external six package.
# This ensures imports like `from ansible.module_utils.six.moves import zip` work.

try:
    # Prefer the bundled six if available
    from ansible.module_utils import six as _bundled_six
    _moves = getattr(_bundled_six, "moves", None)
except Exception:
    _moves = None

if _moves is None:
    # Fallback to external six library
    import importlib
    _moves = importlib.import_module("six.moves")

# Export all attributes of the moves module
globals().update(_moves.__dict__)

# Ensure the module appears as a package
__all__ = list(_moves.__dict__.keys())
