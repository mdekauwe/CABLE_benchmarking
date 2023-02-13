import pytest
from pathlib import Path

from benchcab.benchtree import setup_directory_tree, validate_directory_tree, clean_directory_tree, directory_tree_exists

# Here we use the tmp_path fixture provided by pytest to
# run tests using a temporary directory.


def test_setup_directory_tree(tmp_path):
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


def test_validate_directory_tree(tmp_path):
    # Success case: directory structure should be valid after setup
    setup_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)
    validate_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)

    # Failure case: missing directories should fail
    with pytest.raises(EnvironmentError):
        Path(tmp_path, "runs", "site", "logs").rmdir()
        validate_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)


def test_directory_tree_exists(tmp_path):
    # Success case: directory tree exists after setup
    setup_directory_tree(fluxnet=True, world=False, root_dir=tmp_path)
    assert directory_tree_exists(root_dir=tmp_path)

    # Success case: directory tree does not exist after clean
    clean_directory_tree(root_dir=tmp_path)
    assert not directory_tree_exists(root_dir=tmp_path)
