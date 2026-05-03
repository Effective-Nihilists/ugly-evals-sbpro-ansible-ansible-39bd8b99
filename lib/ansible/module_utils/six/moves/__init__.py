# -*- coding: utf-8 -*-
"""Compatibility shim for ``ansible.module_utils.six.moves``.

The vendored ``six`` implementation expects a ``moves`` package that provides
the standard library modules that were moved between Python 2 and 3.  In this
environment the meta‑path importer used by ``six`` is not activated, resulting
in ``ModuleNotFoundError: No module named 'ansible.module_utils.six.moves'``
when any module imports ``six.moves`` (e.g. ``configparser`` or ``urllib``).

Creating a real package with the required symbols resolves the import error
without altering the vendored ``six`` code.
"""

# Re‑export the most commonly used moved modules.  Additional modules can be
# added here if they are required elsewhere in the code base.

import importlib

# ``configparser`` – the Python 3 name for ``ConfigParser``
configparser = importlib.import_module('configparser')

# ``urllib`` package and its submodules
urllib = importlib.import_module('urllib')
urllib_parse = importlib.import_module('urllib.parse')
urllib_error = importlib.import_module('urllib.error')
urllib_request = importlib.import_module('urllib.request')
urllib_response = importlib.import_module('urllib.response')
urllib_robotparser = importlib.import_module('urllib.robotparser')

# Export a list of public names for ``from ... import *`` semantics.
__all__ = [
    'configparser',
    'urllib',
    'urllib_parse',
    'urllib_error',
    'urllib_request',
    'urllib_response',
    'urllib_robotparser',
]
