"""Contains pytest fixtures accessible to all tests in the same directory."""

import os
import shutil
from pathlib import Path

import pytest

from .common import MOCK_CWD


@pytest.fixture(autouse=True)
def _run_around_tests():
    """`pytest` autouse fixture that runs around each test."""

    # Setup:
    prevdir = Path.cwd()
    if MOCK_CWD.exists():
        shutil.rmtree(MOCK_CWD)
    MOCK_CWD.mkdir()
    os.chdir(MOCK_CWD.expanduser())

    # Run the test:
    yield

    # Teardown:
    os.chdir(prevdir)
    shutil.rmtree(MOCK_CWD)
