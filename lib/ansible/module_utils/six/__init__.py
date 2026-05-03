# Shim for missing six.moves submodule
# Expose the vendored moves package as `moves`
from . import moves as moves

__all__ = ["moves"]
