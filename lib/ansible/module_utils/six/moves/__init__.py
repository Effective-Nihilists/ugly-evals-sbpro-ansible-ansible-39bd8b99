# Compatibility shim for six.moves
from ansible.module_utils.six import moves as _moves
# Re-export all public attributes
for name in dir(_moves):
    if not name.startswith('_'):
        globals()[name] = getattr(_moves, name)

