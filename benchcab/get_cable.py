"""A module containing functions for checking out CABLE repositories."""

import subprocess
from typing import Union
from pathlib import Path

from benchcab import internal


def next_path(path_pattern, sep="-"):
    """Finds the next free path in a sequentially named list of
    files with the following pattern:

    path_pattern = 'file{sep}*.suf':

    file-1.txt
    file-2.txt
    file-3.txt
    """

    loc_pattern = Path(path_pattern)
    new_file_index = 1
    common_filename, _ = loc_pattern.stem.split(sep)

    pattern_files_sorted = sorted(internal.CWD.glob(path_pattern))
    if pattern_files_sorted != []:
        common_filename, last_file_index = pattern_files_sorted[-1].stem.split(sep)
        new_file_index = int(last_file_index) + 1

    return f"{common_filename}{sep}{new_file_index}{loc_pattern.suffix}"


def svn_info_show_item(path: Union[Path, str], item: str) -> str:
    """A wrapper around `svn info --show-item <item> <path>`."""
    cmd = f"svn info --show-item {item} {path}"
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def checkout_cable_auxiliary(verbose=False) -> Path:
    """Checkout CABLE-AUX."""

    cable_aux_dir = Path(internal.CWD / internal.CABLE_AUX_DIR)

    cmd = f"svn checkout {internal.CABLE_SVN_ROOT}/branches/Share/CABLE-AUX {cable_aux_dir}"

    if verbose:
        print(cmd)

    subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=None if verbose else subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    revision = svn_info_show_item(cable_aux_dir, "revision")
    print(f"Successfully checked out CABLE-AUX at revision {revision}")

    # Check relevant files exist in repository:

    if not Path.exists(internal.CWD / internal.GRID_FILE):
        raise RuntimeError(
            f"Error checking out CABLE-AUX: cannot find file '{internal.GRID_FILE}'"
        )

    if not Path.exists(internal.CWD / internal.PHEN_FILE):
        raise RuntimeError(
            f"Error checking out CABLE-AUX: cannot find file '{internal.PHEN_FILE}'"
        )

    if not Path.exists(internal.CWD / internal.CNPBIOME_FILE):
        raise RuntimeError(
            f"Error checking out CABLE-AUX: cannot find file '{internal.CNPBIOME_FILE}'"
        )

    return cable_aux_dir


def checkout_cable(branch_config: dict, verbose=False) -> Path:
    """Checkout a branch of CABLE."""
    # TODO(Sean) do nothing if the repository has already been checked out?
    # This also relates the 'clean' feature.

    cmd = "svn checkout"

    # Check if a specified revision is required. Negative value means take the latest
    if branch_config["revision"] > 0:
        cmd += f" -r {branch_config['revision']}"

    path_to_repo = Path(internal.CWD, internal.SRC_DIR, branch_config["name"])
    cmd += f" {internal.CABLE_SVN_ROOT}/{branch_config['path']} {path_to_repo}"

    if verbose:
        print(cmd)

    subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=None if verbose else subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    revision = svn_info_show_item(path_to_repo, "revision")
    print(f"Successfully checked out {branch_config['name']} at revision {revision}")

    return path_to_repo
