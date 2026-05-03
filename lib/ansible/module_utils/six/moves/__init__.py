# Compatibility shim for ansible.module_utils.six.moves
# Import the virtual moves package from the bundled six implementation and re-export its public symbols.
from ansible.module_utils import six as _six

# Expose the moves namespace as expected.
_moves = _six.moves

# Re-export all public attributes of the moves package (functions, classes, submodules).
for _name in dir(_moves):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_moves, _name)

# Additionally, make submodules (e.g., urllib, urllib_parse) importable via attribute access.
# The six implementation registers them via a meta‑path importer, so simply importing the
# top‑level moves package is sufficient for ``import ansible.module_utils.six.moves.<submodule>``.

