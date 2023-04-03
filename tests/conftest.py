"""Contains pytest fixtures accessible to all tests in the same directory."""

import shutil
import pytest

from .common import TMP_DIR


@pytest.fixture(autouse=True)
def run_around_tests():
    """`pytest` autouse fixture that runs around each test."""

    # Setup:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir()

    # Run the test:
    yield

    # Teardown:
    shutil.rmtree(TMP_DIR)
