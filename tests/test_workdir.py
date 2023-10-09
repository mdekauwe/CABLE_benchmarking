"""`pytest` tests for `workdir.py`."""

import shutil
from pathlib import Path

from benchcab.utils.fs import mkdir
from benchcab.workdir import clean_directory_tree
from tests.common import MOCK_CWD


def setup_mock_fluxsite_directory_list():
    """Return the list of work directories we want benchcab to create"""

    fluxsite_directory_list = [
        Path(MOCK_CWD, "runs", "fluxsite"),
        Path(MOCK_CWD, "runs", "fluxsite", "logs"),
        Path(MOCK_CWD, "runs", "fluxsite", "outputs"),
        Path(MOCK_CWD, "runs", "fluxsite", "tasks"),
        Path(MOCK_CWD, "runs", "fluxsite", "analysis"),
        Path(MOCK_CWD, "runs", "fluxsite", "analysis", "bitwise-comparisons"),
    ]

    return fluxsite_directory_list


def test_setup_directory_tree():
    """Tests for `setup_fluxsite_directory_tree()`."""

    # Success case: generate the full fluxsite directory structure
    setup_fluxsite_directory_tree(root_dir=MOCK_CWD, verbose=True)

    for path in setup_mock_fluxsite_directory_list():
        assert path.exists()

    shutil.rmtree(Path(MOCK_CWD, "runs"))


def test_clean_directory_tree():
    """Tests for `clean_directory_tree()`."""
    # Success case: directory tree does not exist after clean
    setup_fluxsite_directory_tree(root_dir=MOCK_CWD)

    clean_directory_tree(root_dir=MOCK_CWD)
    assert not Path(MOCK_CWD, "runs").exists()

    mkdir(Path(MOCK_CWD, "src"), exist_ok=True)
    clean_directory_tree(root_dir=MOCK_CWD)
    assert not Path(MOCK_CWD, "src").exists()
