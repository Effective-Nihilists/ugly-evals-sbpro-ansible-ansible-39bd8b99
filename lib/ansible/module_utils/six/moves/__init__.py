"""Compatibility shim for six.moves on Python 3.12.
Provides the subset of moved modules required by the Ansible codebase.
"""
import sys
import importlib
import shlex
import functools

# Built‑in moves
map = map  # type: ignore
reduce = functools.reduce
shlex_quote = shlex.quote

# Re‑export selected stdlib modules under the expected names
# configparser
configparser = importlib.import_module('configparser')
# urllib submodules
urllib = importlib.import_module('urllib')
urllib_parse = importlib.import_module('urllib.parse')
urllib_error = importlib.import_module('urllib.error')
urllib_request = importlib.import_module('urllib.request')
urllib_response = importlib.import_module('urllib.response')
urllib_robotparser = importlib.import_module('urllib.robotparser')

# Populate sys.modules for submodule imports like six.moves.urllib.parse
module_name = __name__
submodules = {
    'configparser': configparser,
    'urllib': urllib,
    'urllib.parse': urllib_parse,
    'urllib.error': urllib_error,
    'urllib.request': urllib_request,
    'urllib.response': urllib_response,
    'urllib.robotparser': urllib_robotparser,
}
for name, mod in submodules.items():
    full_name = f"{module_name}.{name}" if not name.startswith('urllib') else f"{module_name}.{name}"  # ensure proper prefix
    sys.modules[full_name] = mod

__all__ = [
    'map', 'reduce', 'shlex_quote',
    'configparser',
    'urllib', 'urllib_parse', 'urllib_error', 'urllib_request',
    'urllib_response', 'urllib_robotparser',
]
