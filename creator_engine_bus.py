"""Compatibility entry point; implementation lives in scripts.creator_engine."""
import sys
from scripts import creator_engine as _implementation

if __name__ == '__main__':
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
