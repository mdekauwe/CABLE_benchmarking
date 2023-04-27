"""`pytest` tests for task.py"""

from pathlib import Path

import pytest

from tests.common import TMP_DIR
from benchcab.build_cable import prepare_build

branch_name = "real1"
compile_dir = "offline"


@pytest.fixture()
def mock_build():
    """Create a fake `build3.ksh` file"""

    # Setup:
    build_path = Path(TMP_DIR, "src", branch_name, compile_dir)
    build_path.mkdir(parents=True)

    build_name = build_path / "build3.sh"
    fname = open(build_name, "w")
    fname.writelines(["module purge\n", "module load something\n"])
    fname.close()

    yield build_path

    # Teardown
    for fname in build_path.glob("*"):
        if fname.is_file():
            fname.unlink()
        else:
            fname.rmdir()
    build_path.rmdir()


def test_prepare_build(mock_build):
    # Success case: uses a user-defined script
    user_script = "/".join([compile_dir, "specified_build.sh"])
    modules = []

    target_path = mock_build.parent / user_script
    target_path.touch()
    assert (
        prepare_build(user_script, branch_name, modules, root_dir=TMP_DIR)
        == target_path
    )

    # Success case: uses the script 'build3.ksh' without modifications if specified as input
    # Test added to remind maintainers of the behaviour.
    user_script = "/".join([compile_dir, "build3.sh"])
    modules = []

    target_path = mock_build.parent / user_script
    target_path.touch()
    assert (
        prepare_build(user_script, branch_name, modules, root_dir=TMP_DIR)
        == target_path
    )

    # Success case: Default behaviour. Returns the modified build script.
    user_script = ""
    modules = []

    target_path = mock_build / "my_build.ksh"
    assert (
        prepare_build(user_script, branch_name, modules, root_dir=TMP_DIR)
        == target_path
    )
