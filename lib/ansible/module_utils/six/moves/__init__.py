# Shim for six.moves
from ansible.module_utils.six import moves as _moves
globals().update(_moves.__dict__)
