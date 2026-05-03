# Minimal six.moves shim for Ansible tests
import configparser as _configparser
import io as _io
import urllib.request as _urllib_request
import urllib.parse as _urllib_parse
import urllib.error as _urllib_error
import collections as _collections
import itertools as _itertools
import builtins as _builtins

# expose common moved names
configparser = _configparser
StringIO = _io.StringIO
urllib_request = _urllib_request
urllib_parse = _urllib_parse
urllib_error = _urllib_error
collections = _collections
itertools = _itertools
builtins = _builtins

def __getattr__(name):
    mapping = {
        'configparser': _configparser,
        'StringIO': _io.StringIO,
        'urllib_request': _urllib_request,
        'urllib_parse': _urllib_parse,
        'urllib_error': _urllib_error,
        'collections': _collections,
        'itertools': _itertools,
        'builtins': _builtins,
    }
    if name in mapping:
        return mapping[name]
    raise AttributeError(name)
