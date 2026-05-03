# Compatibility shim for six.moves
# This package re-exports the dynamically created moves module from ansible.module_utils.six
# It allows imports like `from ansible.module_utils.six.moves import zip` to work.

import os
from .. import moves as _moves
# Export all attributes of the moves module
# Expose the moves module and its attributes
moves = _moves
# Provide common moves symbols expected by Ansible
zip = getattr(_moves, 'zip', __builtins__['zip'])
iteritems = getattr(_moves, 'iteritems', None)
map = getattr(_moves, 'map', None)

