"""Utility functions which wrap around the os module."""

import os
import contextlib
from pathlib import Path


@contextlib.contextmanager
def chdir(newdir: Path):
    """Context manager `cd`."""
    prevdir = Path.cwd()
    os.chdir(newdir.expanduser())
    try:
        yield
    finally:
        os.chdir(prevdir)
