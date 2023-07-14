"""Contains pytest fixtures accessible to all tests in the same directory."""

import shutil
import pytest

from .common import MOCK_CWD


@pytest.fixture(autouse=True)
def run_around_tests():
    """`pytest` autouse fixture that runs around each test."""

    # Setup:
    if MOCK_CWD.exists():
        shutil.rmtree(MOCK_CWD)
    MOCK_CWD.mkdir()

    # Run the test:
    yield

    # Teardown:
    shutil.rmtree(MOCK_CWD)
