"""Project Icecrown: snapshot testing for tabular data.

Freeze a dataset's fingerprint, verify it on every run or pull request, and see which rows,
columns and values moved when it changed.
"""

from importlib.metadata import version as _version

__version__: str = _version("icecrown")
"""The installed version of the package, read from its distribution metadata."""

__all__ = ["__version__"]
