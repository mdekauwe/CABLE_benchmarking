"""`pytest` tests for build_cable.py"""

import unittest.mock
import io
import contextlib
import pytest

from benchcab import internal
from benchcab.build_cable import remove_module_lines, default_build, custom_build
from .common import MOCK_CWD


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


@unittest.mock.patch("benchcab.environment_modules.module_load")
@unittest.mock.patch("benchcab.environment_modules.module_unload")
def test_default_build(
    mock_module_unload, mock_module_load
):  # pylint: disable=unused-argument
    """Tests for `default_build()`."""

    build_script_path = (
        MOCK_CWD / internal.SRC_DIR / "test-branch" / "offline" / "build3.sh"
    )
    build_script_path.parent.mkdir(parents=True)
    build_script_path.touch()

    # Success case: execute the default build command
    with unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        default_build("test-branch", ["foo", "bar"])
        mock_run_cmd.assert_called_once_with("./tmp-build3.sh", verbose=False)

    # Success case: execute the default build command with verbose enabled
    # TODO(Sean): this test should be removed once we use the logging module
    with unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        default_build("test-branch", ["foo", "bar"], verbose=True)
        mock_run_cmd.assert_called_once_with("./tmp-build3.sh", verbose=True)

    # Success case: test non-verbose standard output
    with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            default_build("test-branch", ["foo", "bar"])
        assert buf.getvalue() == (
            "Compiling CABLE serially for realisation test-branch...\n"
        )

    # Success case: test verbose standard output
    with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            default_build("test-branch", ["foo", "bar"], verbose=True)
        assert buf.getvalue() == (
            "Compiling CABLE serially for realisation test-branch...\n"
            f"Copying {build_script_path} to {build_script_path.parent}/tmp-build3.sh\n"
            f"chmod +x {build_script_path.parent}/tmp-build3.sh\n"
            "Modifying tmp-build3.sh: remove lines that call environment "
            "modules\n"
            "Loading modules: foo bar\n"
            "Unloading modules: foo bar\n"
        )

    # Failure case: cannot find default build script
    build_script_path.unlink()
    with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
        with pytest.raises(
            FileNotFoundError,
            match=f"The default build script, {MOCK_CWD}/src/test-branch/offline/build3.sh, "
            "could not be found. Do you need to specify a different build script with the "
            "'build_script' option in config.yaml?",
        ):
            default_build("test-branch", ["foo", "bar"])


def test_custom_build():
    """Tests for `custom_build()`."""

    build_script_path = (
        MOCK_CWD / internal.SRC_DIR / "test-branch" / "offline" / "build3.sh"
    )
    build_script_path.parent.mkdir(parents=True)
    build_script_path.touch()

    # Success case: execute custom build command
    with unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        custom_build(build_script_path, "test-branch")
        mock_run_cmd.assert_called_once_with(
            f"./{build_script_path.name}", verbose=False
        )

    # Success case: execute custom build command with verbose enabled
    # TODO(Sean): this test should be removed once we use the logging module
    with unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        custom_build(build_script_path, "test-branch", verbose=True)
        mock_run_cmd.assert_called_once_with(
            f"./{build_script_path.name}", verbose=True
        )

    # Success case: test non-verbose standard output
    with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            custom_build(build_script_path, "test-branch")
        assert buf.getvalue() == (
            "Compiling CABLE using custom build script for realisation test-branch...\n"
        )

    # Success case: test verbose standard output
    with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            custom_build(build_script_path, "test-branch", verbose=True)
        assert buf.getvalue() == (
            "Compiling CABLE using custom build script for realisation test-branch...\n"
        )
