"""A module containing functions and data structures for manipulating CABLE repositories."""

import shlex
import contextlib
import os
import shutil
import stat
from pathlib import Path
from typing import Optional

from benchcab import internal
from benchcab.environment_modules import EnvironmentModulesInterface, EnvironmentModules
from benchcab.utils.subprocess import SubprocessWrapperInterface, SubprocessWrapper


@contextlib.contextmanager
def chdir(newdir: Path):
    """Context manager `cd`."""
    prevdir = Path.cwd()
    os.chdir(newdir.expanduser())
    try:
        yield
    finally:
        os.chdir(prevdir)


class CableRepository:
    """A class used to represent a CABLE repository."""

    root_dir: Path = internal.CWD
    subprocess_handler: SubprocessWrapperInterface = SubprocessWrapper()
    modules_handler: EnvironmentModulesInterface = EnvironmentModules()

    def __init__(
        self,
        path: str,
        name: Optional[str] = None,
        revision: Optional[int] = None,
        patch: Optional[dict] = None,
        build_script: Optional[str] = None,
        repo_id: Optional[int] = None,
    ) -> None:
        self.path = Path(path)
        self.name = name if name else self.path.name
        self.revision = revision
        self.patch = patch
        self.build_script = build_script
        self._repo_id = repo_id

    @property
    def repo_id(self) -> int:
        """Get or set the repo ID."""
        if self._repo_id is None:
            raise RuntimeError("Attempting to access undefined repo ID")
        return self._repo_id

    @repo_id.setter
    def repo_id(self, value: int):
        self._repo_id = value

    def checkout(self, verbose=False) -> None:
        """Checkout a branch of CABLE."""
        # TODO(Sean) do nothing if the repository has already been checked out?
        # This also relates the 'clean' feature.

        cmd = "svn checkout"

        if self.revision:
            cmd += f" -r {self.revision}"

        path_to_repo = self.root_dir / internal.SRC_DIR / self.name
        cmd += f" {internal.CABLE_SVN_ROOT}/{self.path} {path_to_repo}"

        self.subprocess_handler.run_cmd(cmd, verbose=verbose)

        revision = self.svn_info_show_item("revision")
        print(f"Successfully checked out {self.name} at revision {revision}")

    def svn_info_show_item(self, item: str) -> str:
        """A wrapper around `svn info --show-item <item> <path-to-repo>`."""
        path_to_repo = self.root_dir / internal.SRC_DIR / self.name
        proc = self.subprocess_handler.run_cmd(
            f"svn info --show-item {item} {path_to_repo}", capture_output=True
        )
        return proc.stdout.strip()

    # TODO(Sean) the modules argument should be in the constructor and
    # `custom_build()` should be a part of `build()`. This is part of
    # issue #94.
    def build(self, modules: list[str], verbose=False) -> None:
        """Build CABLE using the default script."""

        print(
            f"Compiling CABLE {'with MPI' if internal.MPI else 'serially'} for "
            f"realisation {self.name}..."
        )

        default_script_path = (
            self.root_dir / internal.SRC_DIR / self.name / "offline" / "build3.sh"
        )

        if not default_script_path.is_file():
            raise FileNotFoundError(
                f"The default build script, {default_script_path}, could not be found. "
                "Do you need to specify a different build script with the "
                "'build_script' option in config.yaml?",
            )

        tmp_script_path = default_script_path.parent / "tmp-build3.sh"

        if verbose:
            print(f"Copying {default_script_path} to {tmp_script_path}")
        shutil.copy(default_script_path, tmp_script_path)

        if verbose:
            print(f"chmod +x {tmp_script_path}")
        tmp_script_path.chmod(tmp_script_path.stat().st_mode | stat.S_IEXEC)

        if verbose:
            print(
                f"Modifying {tmp_script_path.name}: remove lines that call "
                "environment modules"
            )
        remove_module_lines(tmp_script_path)

        with chdir(default_script_path.parent), self.modules_handler.load(
            modules, verbose=verbose
        ):
            self.subprocess_handler.run_cmd(
                f"./{tmp_script_path.name}" + (" mpi" if internal.MPI else ""),
                verbose=verbose,
            )

    def custom_build(self, verbose=False) -> None:
        """Build CABLE with a script provided in configuration file"""

        if self.build_script is None:
            # TODO(Sean) it is bad that we are allowing this to fail silently
            # but this will be fixed once we have a single build function.
            return

        print(
            "Compiling CABLE using custom build script for "
            f"realisation {self.name}..."
        )

        build_script_path = (
            self.root_dir / internal.SRC_DIR / self.name / self.build_script
        )

        with chdir(build_script_path.parent):
            self.subprocess_handler.run_cmd(
                f"./{build_script_path.name}", verbose=verbose
            )


def remove_module_lines(file_path: Path) -> None:
    """Remove lines from `file_path` that call the environment modules package."""
    with file_path.open("r", encoding="utf-8") as file:
        contents = file.read()
    with file_path.open("w", encoding="utf-8") as file:
        for line in contents.splitlines(True):
            cmds = shlex.split(line, comments=True)
            if "module" not in cmds:
                file.write(line)
