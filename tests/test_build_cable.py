"""`pytest` tests for build_cable.py"""

import subprocess
import unittest.mock
import io
import contextlib
import pytest

from benchcab import internal
from benchcab.build_cable import patch_build_script, default_build, custom_build
from benchcab import environment_modules
from .common import MOCK_CWD


def test_patch_build_script():
    """Tests for `patch_build_script()`."""
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

    patch_build_script(file_path)

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


def test_default_build():
    """Tests for `default_build()`."""
    offline_dir = MOCK_CWD / internal.SRC_DIR / "test-branch" / "offline"
    offline_dir.mkdir(parents=True)
    build_script_path = offline_dir / "build3.sh"
    build_script_path.touch()

    # Success case: execute the default build command
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run:
        default_build("test-branch", ["foo", "bar"])
        mock_subprocess_run.assert_called_once_with(
            "./tmp-build3.sh",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(
        io.StringIO()
    ) as buf:
        default_build("test-branch", ["foo", "bar"])
    assert buf.getvalue() == (
        "Compiling CABLE serially for realisation test-branch...\n"
    )

    # Success case: test verbose output
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(
        io.StringIO()
    ) as buf:
        default_build("test-branch", ["foo", "bar"], verbose=True)
        mock_subprocess_run.assert_called_once_with(
            "./tmp-build3.sh",
            shell=True,
            check=True,
            stdout=None,
            stderr=subprocess.STDOUT,
        )
    assert buf.getvalue() == (
        "Compiling CABLE serially for realisation test-branch...\n"
        f"  Copying {build_script_path} to {build_script_path.parent}/tmp-build3.sh\n"
        f"  chmod +x {build_script_path.parent}/tmp-build3.sh\n"
        "  Patching tmp-build3.sh: remove lines that call environment "
        "modules\n"
        f"  Loading modules: foo bar\n"
        f"  ./tmp-build3.sh\n"
        f"  Unloading modules: foo bar\n"
    )

    # Failure case: cannot load modules
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ) as mock_module_load, unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run:
        mock_module_load.side_effect = environment_modules.EnvironmentModulesError
        with pytest.raises(environment_modules.EnvironmentModulesError):
            default_build("test-branch", ["foo", "bar"])

    # Failure case: cannot unload modules
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ) as mock_module_unload, unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run:
        mock_module_unload.side_effect = environment_modules.EnvironmentModulesError
        with pytest.raises(environment_modules.EnvironmentModulesError):
            default_build("test-branch", ["foo", "bar"])

    # Failure case: cannot find default build script
    build_script_path.unlink()
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run:
        with pytest.raises(
            FileNotFoundError,
            match=f"The default build script, {MOCK_CWD}/src/test-branch/offline/build3.sh, "
            "could not be found. Do you need to specify a different build script with the "
            "'build_script' option in config.yaml?",
        ):
            default_build("test-branch", ["foo", "bar"], verbose=True)


def test_custom_build():
    """Tests for `custom_build()`."""
    offline_dir = MOCK_CWD / internal.SRC_DIR / "test-branch" / "offline"
    offline_dir.mkdir(parents=True)
    build_script_path = offline_dir / "custom-build.sh"
    build_script_path.touch()

    # Success case: execute custom build command
    with unittest.mock.patch(
        "benchcab.environment_modules.module_load"
    ), unittest.mock.patch(
        "benchcab.environment_modules.module_unload"
    ), unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run:
        custom_build(build_script_path, "test-branch")
        mock_subprocess_run.assert_called_once_with(
            f"./{build_script_path.name}",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
        custom_build(build_script_path, "test-branch")
    assert buf.getvalue() == (
        "Compiling CABLE using custom build script for realisation test-branch...\n"
    )

    # Success case: test verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
        custom_build(build_script_path, "test-branch", verbose=True)
        mock_subprocess_run.assert_called_once_with(
            f"./{build_script_path.name}",
            shell=True,
            check=True,
            stdout=None,
            stderr=subprocess.STDOUT,
        )
    assert buf.getvalue() == (
        "Compiling CABLE using custom build script for realisation test-branch...\n"
        f"  ./{build_script_path.name}\n"
    )
