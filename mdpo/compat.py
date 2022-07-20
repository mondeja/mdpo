"""Compatibilities for different versions of Python."""

import sys


if sys.version_info < (3, 10):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

__all__ = (
    'importlib_metadata',
)
