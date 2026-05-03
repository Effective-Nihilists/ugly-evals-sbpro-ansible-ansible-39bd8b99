# Stub moves package for ansible.module_utils.six
# Provides compatibility shims using Python 3 stdlib equivalents.

# Modules
import importlib
configparser = importlib.import_module('configparser')
queue = importlib.import_module('queue')
builtins = importlib.import_module('builtins')

# Functions and aliases
from shlex import quote as shlex_quote
from itertools import zip_longest

# Compatibility aliases
xrange = range
map = builtins.map
reduce = builtins.reduce
zip = builtins.zip

# cPickle compatibility
import pickle as cPickle

# StringIO
from io import StringIO

# Expose urllib subpackage as a namespace package
import types
urllib = types.ModuleType('urllib')
# Populate urllib namespace with submodules (parse, error, request, response, robotparser)
urllib.parse = importlib.import_module('urllib.parse')
urllib.error = importlib.import_module('urllib.error')
urllib.request = importlib.import_module('urllib.request')
urllib.response = importlib.import_module('urllib.response')
urllib.robotparser = importlib.import_module('urllib.robotparser')

# Make submodules importable via package path
import sys
sys.modules[__name__ + '.urllib'] = urllib
sys.modules[__name__ + '.urllib.parse'] = urllib.parse
sys.modules[__name__ + '.urllib.error'] = urllib.error
sys.modules[__name__ + '.urllib.request'] = urllib.request
sys.modules[__name__ + '.urllib.response'] = urllib.response
sys.modules[__name__ + '.urllib.robotparser'] = urllib.robotparser

__all__ = [
    'configparser', 'queue', 'builtins', 'shlex_quote', 'zip_longest',
    'xrange', 'map', 'reduce', 'zip', 'cPickle', 'StringIO', 'urllib'
]
