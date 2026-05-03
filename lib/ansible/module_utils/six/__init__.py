# Minimal stub for ansible.module_utils.six
try:
    import six as _six
except ImportError:
    # Fallback minimal definitions
    import sys
    class _Six:
        PY3 = sys.version_info[0] == 3
        PY2 = sys.version_info[0] == 2
        # Provide basic types
        string_types = (str,)
        binary_type = bytes
        text_type = str
        integer_types = (int,)
        class _LazyObject:
            pass
    _six = _Six()
# Export six attributes
globals().update(_six.__dict__)
# Provide moves subpackage
from types import ModuleType
import importlib
_moves = importlib.import_module('six.moves') if 'six' in globals() else None
if _moves:
    moves = _moves
else:
    moves = ModuleType('moves')
    # minimal placeholder attributes
    # common moves used in codebase
    import configparser, urllib.parse, urllib.error, shlex, itertools
    moves.configparser = configparser
    moves.urllib = urllib
    moves.urllib.parse = urllib.parse
    moves.urllib.error = urllib.error
    moves.shlex_quote = shlex.quote
    moves.zip = zip
    moves.reduce = getattr(__import__('functools'), 'reduce')
    moves.map = map
    moves.xrange = range
    # expose as module attributes
    globals()['moves'] = moves
