# Stub package to expose six.moves submodule
# This ensures imports like "ansible.module_utils.six.moves" succeed.
# It re-exports the dynamically created moves module from the parent six package.
from .. import moves as _moves
# Populate module namespace with attributes from the moves object
globals().update(_moves.__dict__)
# Clean up temporary name
del _moves
