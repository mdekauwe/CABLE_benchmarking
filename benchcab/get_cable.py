#!/usr/bin/env python

"""
Get the head of the CABLE trunk, the user branch and CABLE-AUX

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (09.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import subprocess
import getpass
from typing import Union
from pathlib import Path

from benchcab import internal
from benchcab.internal import CWD, SRC_DIR, HOME_DIR, CABLE_SVN_ROOT, CABLE_AUX_DIR


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

    pattern_files_sorted = sorted(Path('.').glob(path_pattern))
    if len(pattern_files_sorted):
        common_filename, last_file_index = pattern_files_sorted[-1].stem.split(sep)
        new_file_index = int(last_file_index) + 1

    return f"{common_filename}{sep}{new_file_index}{loc_pattern.suffix}"


def archive_rev_number():
    """Archives previous rev_number.log"""

    revision_file = Path("rev_number.log")
    if revision_file.exists():
        revision_file.replace(next_path("rev_number-*.log"))


def need_pass() -> bool:
    """If the user requires a password for SVN, return `True`. Otherwise return `False`."""
    try:
        return os.listdir(f"{HOME_DIR}/.subversion/auth/svn.simple/") == []
    except FileNotFoundError:
        return False


def get_password() -> str:
    """Prompt user for a password."""
    return "'" + getpass.getpass("Password:") + "'"


def svn_info_show_item(path: Union[Path, str], item: str) -> str:
    """A wrapper around `svn info --show-item <item> <path>`."""
    cmd = f"svn info --show-item {item} {path}"
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def checkout_cable_auxiliary():
    """Checkout CABLE-AUX."""
    # TODO(Sean) we should archive revision numbers for CABLE-AUX

    cable_aux_dir = Path(CWD / CABLE_AUX_DIR)
    if cable_aux_dir.exists():
        return

    cmd = f"svn checkout {CABLE_SVN_ROOT}/branches/Share/CABLE-AUX {cable_aux_dir}"

    if need_pass():
        cmd += f" --password {get_password()}"

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        print(f"Error checking out CABLE-AUX: {err.cmd}")
        raise

    # Check relevant files exist in repository:

    if not Path.exists(CWD / internal.GRID_FILE):
        raise RuntimeError(f"Error checking out CABLE-AUX: cannot find file '{internal.GRID_FILE}'")

    if not Path.exists(CWD / internal.PHEN_FILE):
        raise RuntimeError(f"Error checking out CABLE-AUX: cannot find file '{internal.PHEN_FILE}'")

    if not Path.exists(CWD / internal.CNPBIOME_FILE):
        raise RuntimeError(
            f"Error checking out CABLE-AUX: cannot find file '{internal.CNPBIOME_FILE}'"
        )


def checkout_cable(branch_config: dict, user: str):
    """Checkout a branch of CABLE."""
    # TODO(Sean) do nothing if the repository has already been checked out?
    # This also relates the 'clean' feature.

    cmd = "svn checkout"

    # Check if a specified revision is required. Negative value means take the latest
    if branch_config["revision"] > 0:
        cmd += f" -r {branch_config['revision']}"

    if branch_config["trunk"]:
        path_to_repo = Path(CWD, SRC_DIR, "trunk")
        cmd += f" {CABLE_SVN_ROOT}/trunk {path_to_repo}"
    elif branch_config["share_branch"]:
        path_to_repo = Path(CWD, SRC_DIR, branch_config["name"])
        cmd += f" {CABLE_SVN_ROOT}/branches/Share/{branch_config['name']} {path_to_repo}"
    else:
        path_to_repo = Path(CWD, SRC_DIR, branch_config["name"])
        cmd += f" {CABLE_SVN_ROOT}/branches/Users/{user}/{branch_config['name']} {path_to_repo}"

    if need_pass():
        cmd += f" --password {get_password()}"

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        print(f"Error checking out {branch_config['name']}: {err.cmd}")
        raise

    # Write last change revision number to rev_number.log file
    rev_number = svn_info_show_item(path_to_repo, "last-changed-revision")
    with open(f"{CWD}/rev_number.log", "a", encoding="utf-8") as fout:
        fout.write(f"{branch_config['name']} last change revision: {rev_number}\n")
