# Shim for ansible.module_utils.six to re-export the external 'six' package
import six as _six
import sys
# Expose the six module's attributes at this package level
for name in dir(_six):
    if not name.startswith('_'):
        globals()[name] = getattr(_six, name)
# Ensure that "ansible.module_utils.six.moves" resolves to six.moves
sys.modules[__name__ + ".moves"] = _six.moves
