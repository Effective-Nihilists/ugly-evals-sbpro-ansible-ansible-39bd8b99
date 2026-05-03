# Compatibility shim for ansible.module_utils.six.moves
from ansible.module_utils import six as _six
_moves = _six.moves
# Re-export public symbols
for _name in dir(_moves):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_moves, _name)
