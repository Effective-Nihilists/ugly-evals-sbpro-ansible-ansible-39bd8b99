import six as _six
import sys
# Make this a package
globals().update(_six.__dict__)
if hasattr(_six, 'moves'):
    sys.modules[__name__ + '.moves'] = _six.moves
