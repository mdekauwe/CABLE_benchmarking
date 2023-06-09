"""A module containing functions for building CABLE."""

import os
import contextlib
import stat
import subprocess
import shlex
import shutil
import pathlib

from benchcab import internal
from benchcab import environment_modules


@contextlib.contextmanager
def chdir(newdir: pathlib.Path):
    """Context manager `cd`."""
    prevdir = pathlib.Path.cwd()
    os.chdir(newdir.expanduser())
    try:
        yield
    finally:
        os.chdir(prevdir)


def patch_build_script(file_path):
    """Remove lines from `file_path` that call the environment modules package."""
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read()
    with open(file_path, "w", encoding="utf-8") as file:
        for line in contents.splitlines(True):
            cmds = shlex.split(line, comments=True)
            if "module" not in cmds:
                file.write(line)


def default_build(branch_name: str, modules: list, verbose=False):
    """Build CABLE using the default script.

    This loads the modules specified in the configuration file.
    """
    print(
        f"Compiling CABLE {'with MPI' if internal.MPI else 'serially'} for "
        f"realisation {branch_name}..."
    )

    default_script_path = (
        internal.CWD / internal.SRC_DIR / branch_name / "offline" / "build3.sh"
    )

    if not default_script_path.is_file():
        raise FileNotFoundError(
            f"The default build script, {default_script_path}, could not be found. "
            "Do you need to specify a different build script with the "
            "'build_script' option in config.yaml?",
        )

    tmp_script_path = default_script_path.parent / "tmp-build3.sh"

    if verbose:
        print(f"  Copying {default_script_path} to {tmp_script_path}")
    shutil.copy(default_script_path, tmp_script_path)
    if verbose:
        print(f"  chmod +x {tmp_script_path}")
    tmp_script_path.chmod(tmp_script_path.stat().st_mode | stat.S_IEXEC)

    if verbose:
        print(
            f"  Patching {tmp_script_path.name}: remove lines that call "
            "environment modules"
        )
    patch_build_script(tmp_script_path)

    if verbose:
        print("  Loading modules: " + " ".join(modules))
    environment_modules.module_load(*modules)

    with chdir(default_script_path.parent):
        cmd = f"./{tmp_script_path.name}" + (" mpi" if internal.MPI else "")
        if verbose:
            print(f"  {cmd}")
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    if verbose:
        print("  Unloading modules: " + " ".join(modules))
    environment_modules.module_unload(*modules)


def custom_build(config_build_script: str, branch_name: str, verbose=False):
    """Build CABLE with a script provided in configuration file"""
    print(
        "Compiling CABLE using custom build script for " f"realisation {branch_name}..."
    )

    build_script_path = (
        internal.CWD / internal.SRC_DIR / branch_name / config_build_script
    )

    with chdir(build_script_path.parent):
        cmd = f"./{build_script_path.name}"
        if verbose:
            print(f"  {cmd}")
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
