# Simplified six shim for Ansible
# This file provides the ansible.module_utils.six package by delegating to the external six library.
# It ensures that imports like `from ansible.module_utils.six.moves import zip` work.

import six as _six
# expose top-level attributes
globals().update(_six.__dict__)

# expose moves submodule
try:
    from six import moves as moves
except ImportError:
    # fallback: create empty moves namespace
    class _EmptyMoves:
        pass
    moves = _EmptyMoves()
