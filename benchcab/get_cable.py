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
import shlex
import getpass
import tempfile
from pathlib import Path

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


def checkout_cable(branch_config: dict, user: str):

    # TODO(Sean) checking out CABLE-AUX should be in a separate function
    # TODO(Sean) can we avoid code repetition for the trunk and dev branch?

    src_dir = Path(CWD / SRC_DIR)
    if not src_dir.exists():
        os.makedirs(src_dir)

    os.chdir(src_dir)

    need_pass = False

    # Check if a specified version is required. Negative value means take the latest
    rev_opt = ""
    if branch_config['revision'] > 0:
        rev_opt = f"-r {branch_config['revision']}"

    try:
        where = os.listdir("%s/.subversion/auth/svn.simple/" % (HOME_DIR))
        if len(where) == 0:
            pswd = "'" + getpass.getpass("Password:") + "'"
            need_pass = True
    except FileNotFoundError:
        pswd = "'" + getpass.getpass("Password:") + "'"
        need_pass = True

    # Checkout the head of the trunk ...
    if branch_config['trunk']:

        if need_pass:
            cmd = f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/trunk --password {pswd}"

            with tempfile.NamedTemporaryFile(mode="w+t") as f:
                f.write(cmd)
                f.flush()

                error = subprocess.call(["/bin/bash", f.name])
                if error == 1:
                    raise ("Error downloading repo")
                f.close()
        else:
            cmd = f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/trunk"

            error = subprocess.call(cmd, shell=True)
            if error == 1:
                raise ("Error downloading repo")

    # Checkout named branch ...
    else:

        if need_pass:

            if branch_config['share_branch']:
                cmd = f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/branches/Share/{branch_config['name']} --password {pswd}"
            else:
                cmd = f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/branches/Users/{user}/{branch_config['name']} --password {pswd}"

            with tempfile.NamedTemporaryFile(mode="w+t") as f:
                f.write(cmd)
                f.flush()

                error = subprocess.call(["/bin/bash", f.name])
                if error == 1:
                    raise ("Error downloading repo")
                f.close()
        else:
            if branch_config['share_branch']:
                cmd = (
                    f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/branches/Share/{branch_config['name']}"
                )
            else:
                cmd = f"svn checkout {rev_opt} {CABLE_SVN_ROOT}/branches/Users/{user}/{branch_config['name']}"

            error = subprocess.call(cmd, shell=True)
            if error == 1:
                raise ("Error downloading repo")

    # Checkout CABLE-AUX
    cable_aux_dir = Path(CWD / CABLE_AUX_DIR)
    if not cable_aux_dir.exists():
        if need_pass:
            cmd = f"svn checkout {CABLE_SVN_ROOT}/branches/Share/CABLE-AUX CABLE-AUX --password {pswd}"
            with tempfile.NamedTemporaryFile(mode="w+t") as f:
                f.write(cmd)
                f.flush()

                error = subprocess.call(["/bin/bash", f.name])
                if error == 1:
                    raise ("Error checking out CABLE-AUX")
                f.close()
        else:
            cmd = f"svn checkout {CABLE_SVN_ROOT}/branches/Share/CABLE-AUX CABLE-AUX"

            error = subprocess.call(cmd, shell=True)
            if error == 1:
                raise ("Error checking out CABLE-AUX")

    # Write last change revision number to rev_number.log file
    cmd = shlex.split(f"svn info --show-item last-changed-revision {branch_config['name']}")
    out = subprocess.run(cmd, capture_output=True, text=True)
    rev_number = out.stdout
    with open(f"{CWD}/rev_number.log", "a") as fout:
        fout.write(f"{branch_config['name']} last change revision: {rev_number}")
    os.chdir(CWD)
