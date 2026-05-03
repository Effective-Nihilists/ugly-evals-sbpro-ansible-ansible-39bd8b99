# expose six.moves as a package
from .. import moves as _moves
globals().update(_moves.__dict__)
