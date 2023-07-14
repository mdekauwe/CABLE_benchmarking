"""`pytest` tests for repository.py"""

import io
import contextlib
import pytest

from benchcab import internal
from benchcab.environment_modules import EnvironmentModulesInterface
from benchcab.utils.subprocess import SubprocessWrapperInterface
from benchcab.repository import CableRepository, remove_module_lines
from .common import MOCK_CWD, MockEnvironmentModules, MockSubprocessWrapper


def get_mock_repo(
    subprocess_handler: SubprocessWrapperInterface = MockSubprocessWrapper(),
    modules_handler: EnvironmentModulesInterface = MockEnvironmentModules(),
) -> CableRepository:
    """Returns a mock `CableRepository` instance for testing against."""
    repo = CableRepository(path="trunk")
    repo.root_dir = MOCK_CWD
    repo.subprocess_handler = subprocess_handler
    repo.modules_handler = modules_handler
    return repo


def test_repo_id():
    """Tests for `CableRepository.repo_id`."""

    # Success case: get repository ID
    repo = CableRepository("path/to/repo", repo_id=123)
    assert repo.repo_id == 123

    # Success case: set repository ID
    repo = CableRepository("path/to/repo", repo_id=123)
    repo.repo_id = 456
    assert repo.repo_id == 456

    # Failure case: access undefined repository ID
    repo = CableRepository("path/to/repo")
    with pytest.raises(RuntimeError, match="Attempting to access undefined repo ID"):
        _ = repo.repo_id


def test_checkout():
    """Tests for `CableRepository.checkout()`."""

    # Success case: checkout mock repository
    mock_subprocess = MockSubprocessWrapper()
    repo = get_mock_repo(mock_subprocess)
    repo.checkout()
    assert (
        f"svn checkout https://trac.nci.org.au/svn/cable/trunk {MOCK_CWD}/src/trunk"
        in mock_subprocess.commands
    )

    # Success case: checkout mock repository with specified revision number
    mock_subprocess = MockSubprocessWrapper()
    repo = get_mock_repo(mock_subprocess)
    repo.revision = 9000
    repo.checkout()
    assert (
        f"svn checkout -r 9000 https://trac.nci.org.au/svn/cable/trunk {MOCK_CWD}/src/trunk"
        in mock_subprocess.commands
    )

    # Success case: test non-verbose standard output
    mock_subprocess = MockSubprocessWrapper()
    repo = get_mock_repo(mock_subprocess)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.checkout()
    assert (
        buf.getvalue()
        == f"Successfully checked out trunk at revision {mock_subprocess.stdout}\n"
    )

    # Success case: test verbose standard output
    mock_subprocess = MockSubprocessWrapper()
    repo = get_mock_repo(mock_subprocess)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.checkout(verbose=True)
    assert (
        buf.getvalue()
        == f"Successfully checked out trunk at revision {mock_subprocess.stdout}\n"
    )


def test_svn_info_show_item():
    """Tests for `CableRepository.svn_info_show_item()`."""

    # Success case: call svn info command and get result
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.stdout = "mock standard output"
    repo = get_mock_repo(mock_subprocess)
    assert repo.svn_info_show_item("some-mock-item") == mock_subprocess.stdout
    assert (
        f"svn info --show-item some-mock-item {MOCK_CWD}/src/trunk"
        in mock_subprocess.commands
    )

    # Success case: test leading and trailing white space is removed from standard output
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.stdout = " \n\n mock standard output \n\n"
    repo = get_mock_repo(mock_subprocess)
    assert repo.svn_info_show_item("some-mock-item") == mock_subprocess.stdout.strip()
    assert (
        f"svn info --show-item some-mock-item {MOCK_CWD}/src/trunk"
        in mock_subprocess.commands
    )


def test_build():
    """Tests for `CableRepository.build()`."""
    build_script_path = MOCK_CWD / internal.SRC_DIR / "trunk" / "offline" / "build3.sh"
    build_script_path.parent.mkdir(parents=True)
    build_script_path.touch()
    mock_modules = ["foo", "bar"]

    # Success case: execute the default build command
    mock_subprocess = MockSubprocessWrapper()
    mock_environment_modules = MockEnvironmentModules()
    repo = get_mock_repo(mock_subprocess, mock_environment_modules)
    repo.build(mock_modules)
    assert "./tmp-build3.sh" in mock_subprocess.commands
    assert (
        "module load " + " ".join(mock_modules)
    ) in mock_environment_modules.commands
    assert (
        "module unload " + " ".join(mock_modules)
    ) in mock_environment_modules.commands

    # Success case: test non-verbose standard output
    repo = get_mock_repo()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.build(mock_modules)
    assert buf.getvalue() == ("Compiling CABLE serially for realisation trunk...\n")

    # Success case: test verbose standard output
    repo = get_mock_repo()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.build(mock_modules, verbose=True)
    assert buf.getvalue() == (
        "Compiling CABLE serially for realisation trunk...\n"
        f"Copying {build_script_path} to {build_script_path.parent}/tmp-build3.sh\n"
        f"chmod +x {build_script_path.parent}/tmp-build3.sh\n"
        "Modifying tmp-build3.sh: remove lines that call environment "
        "modules\n"
        f"Loading modules: {' '.join(mock_modules)}\n"
        f"Unloading modules: {' '.join(mock_modules)}\n"
    )

    # Failure case: cannot find default build script
    build_script_path.unlink()
    repo = get_mock_repo()
    with pytest.raises(
        FileNotFoundError,
        match=f"The default build script, {MOCK_CWD}/src/trunk/offline/build3.sh, "
        "could not be found. Do you need to specify a different build script with the "
        "'build_script' option in config.yaml?",
    ):
        repo.build(mock_modules)


def test_custom_build():
    """Tests for `custom_build()`."""

    build_script = "offline/build.sh"
    build_script_path = MOCK_CWD / internal.SRC_DIR / "trunk" / build_script
    build_script_path.parent.mkdir(parents=True)
    build_script_path.touch()

    # Success case: execute custom build command
    mock_subprocess = MockSubprocessWrapper()
    repo = get_mock_repo(subprocess_handler=mock_subprocess)
    repo.build_script = build_script
    repo.custom_build()
    assert f"./{build_script_path.name}" in mock_subprocess.commands

    # Success case: test non-verbose standard output
    repo = get_mock_repo()
    repo.build_script = build_script
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.custom_build()
    assert buf.getvalue() == (
        "Compiling CABLE using custom build script for realisation trunk...\n"
    )

    # Success case: test verbose standard output
    repo = get_mock_repo()
    repo.build_script = build_script
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        repo.custom_build(verbose=True)
    assert buf.getvalue() == (
        "Compiling CABLE using custom build script for realisation trunk...\n"
    )


def test_remove_module_lines():
    """Tests for `remove_module_lines()`."""

    # Success case: test 'module' lines are removed from mock shell script
    file_path = MOCK_CWD / "test-build.sh"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            """#!/bin/bash
module add bar
module purge

host_gadi()
{
   . /etc/bashrc
   module purge
   module add intel-compiler/2019.5.281
   module add netcdf/4.6.3
   module load foo
   modules
   echo foo && module load
   echo foo # module load
   # module load foo

   if [[ $1 = 'mpi' ]]; then
      module add intel-mpi/2019.5.281
   fi
}
"""
        )

    remove_module_lines(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        assert file.read() == (
            """#!/bin/bash

host_gadi()
{
   . /etc/bashrc
   modules
   echo foo # module load
   # module load foo

   if [[ $1 = 'mpi' ]]; then
   fi
}
"""
        )
