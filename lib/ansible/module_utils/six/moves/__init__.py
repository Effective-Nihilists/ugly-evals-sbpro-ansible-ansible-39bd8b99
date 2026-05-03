# Compatibility shim for six.moves
# This package re-exports the dynamically created moves module from ansible.module_utils.six
# It allows imports like `from ansible.module_utils.six.moves import zip` to work.

from .. import moves as _moves
# Export all attributes of the moves module
globals().update(_moves.__dict__)
