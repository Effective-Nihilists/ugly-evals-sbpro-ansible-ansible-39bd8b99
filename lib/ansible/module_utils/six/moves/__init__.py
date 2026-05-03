# Compatibility shim for ansible.module_utils.six.moves

from .. import moves

# Re-export public symbols from six.moves
for _name in dir(moves):
    if not _name.startswith('_'):
        globals()[_name] = getattr(moves, _name)
