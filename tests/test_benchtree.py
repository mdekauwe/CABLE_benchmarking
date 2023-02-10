import pytest
from pathlib import Path

from benchcab.benchtree import setup_directory_tree

# Here we use the tmp_path fixture provided by pytest to
# run tests using a temporary directory.


def test_setup_directory_tree(tmp_path):
    assert len(list(tmp_path.glob("*"))) == 0

    # Success case: generate fluxnet directory structure
    setup_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)
    assert len(list(tmp_path.glob("*"))) == 2
    assert Path(tmp_path, "src").exists()
    assert Path(tmp_path, "runs").exists()
    assert Path(tmp_path, "runs", "site").exists()
    assert Path(tmp_path, "runs", "site", "logs").exists()
    assert Path(tmp_path, "runs", "site", "namelists").exists()
    assert Path(tmp_path, "runs", "site", "outputs").exists()
    assert Path(tmp_path, "runs", "site", "restart_files").exists()

    # Success case: calling setup_directory_tree() should do nothing if
    # a valid directory structure already exists
    setup_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)
    assert len(list(tmp_path.glob("*"))) == 2
    assert Path(tmp_path, "src").exists()
    assert Path(tmp_path, "runs").exists()
    assert Path(tmp_path, "runs", "site").exists()
    assert Path(tmp_path, "runs", "site", "logs").exists()
    assert Path(tmp_path, "runs", "site", "namelists").exists()
    assert Path(tmp_path, "runs", "site", "outputs").exists()
    assert Path(tmp_path, "runs", "site", "restart_files").exists()

    # Success case: cleaning and generating directory structure should
    # do nothing
    setup_directory_tree(fluxnet=True, world=False, root_dir=tmp_path, clean=True)
    assert len(list(tmp_path.glob("*"))) == 2
    assert Path(tmp_path, "src").exists()
    assert Path(tmp_path, "runs").exists()
    assert Path(tmp_path, "runs", "site").exists()
    assert Path(tmp_path, "runs", "site", "logs").exists()
    assert Path(tmp_path, "runs", "site", "namelists").exists()
    assert Path(tmp_path, "runs", "site", "outputs").exists()
    assert Path(tmp_path, "runs", "site", "restart_files").exists()

    # TODO(Sean) Failure case: missing directories should fail
    with pytest.raises(EnvironmentError):
        pass


def test_clean_directory_tree(tmp_path):
    assert len(list(tmp_path.glob("*"))) == 0

    # TODO(Sean) Success case: generate and clean fluxnet directory structure
