"""`pytest` tests for `workdir.py`."""

import shutil
from pathlib import Path

import pytest

from benchcab.utils.fs import mkdir
from benchcab.workdir import (
    clean_directory_tree,
    setup_fluxsite_directory_tree,
)


def setup_mock_fluxsite_directory_list():
    """Return the list of work directories we want benchcab to create."""
    fluxsite_directory_list = [
        Path("runs", "fluxsite"),
        Path("runs", "fluxsite", "logs"),
        Path("runs", "fluxsite", "outputs"),
        Path("runs", "fluxsite", "tasks"),
        Path("runs", "fluxsite", "analysis"),
        Path("runs", "fluxsite", "analysis", "bitwise-comparisons"),
    ]

    return fluxsite_directory_list


def test_setup_directory_tree():
    """Tests for `setup_fluxsite_directory_tree()`."""
    # Success case: generate the full fluxsite directory structure
    setup_fluxsite_directory_tree()

    for path in setup_mock_fluxsite_directory_list():
        assert path.exists()

    shutil.rmtree(Path("runs"))


@pytest.mark.parametrize("test_path", [Path("runs"), Path("src")])
def test_clean_directory_tree(test_path):
    """Tests for `clean_directory_tree()`."""
    # Success case: directory tree does not exist after clean
    mkdir(test_path)
    clean_directory_tree()
    assert not test_path.exists()
