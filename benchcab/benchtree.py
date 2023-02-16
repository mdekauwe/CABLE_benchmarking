"""Contains functions for generating the directory structure used for `benchcab`."""
from pathlib import Path
import os
import shutil

from benchcab import internal


def clean_directory_tree(root_dir=internal.CWD):
    """Remove pre-existing directories in `root_dir`."""
    src_dir = Path(root_dir, internal.SRC_DIR)
    if src_dir.exists():
        shutil.rmtree(src_dir)

    run_dir = Path(root_dir, internal.RUN_DIR)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def setup_directory_tree(fluxnet: bool, world: bool, root_dir=internal.CWD, clean=False):
    """Generate the directory structure used of `benchcab`."""
    if clean:
        clean_directory_tree(root_dir)

    src_dir = Path(root_dir, internal.SRC_DIR)
    if not src_dir.exists():
        os.makedirs(src_dir)

    run_dir = Path(root_dir, internal.RUN_DIR)
    if not run_dir.exists():
        os.makedirs(run_dir)

    if fluxnet:
        site_run_dir = Path(root_dir, internal.SITE_RUN_DIR)
        if not site_run_dir.exists():
            os.makedirs(site_run_dir)

        site_log_dir = Path(root_dir, internal.SITE_LOG_DIR)
        if not site_log_dir.exists():
            os.makedirs(site_log_dir)

        site_output_dir = Path(root_dir, internal.SITE_OUTPUT_DIR)
        if not site_output_dir.exists():
            os.makedirs(site_output_dir)

        site_restart_dir = Path(root_dir, internal.SITE_RESTART_DIR)
        if not site_restart_dir.exists():
            os.makedirs(site_restart_dir)

        site_namelist_dir = Path(root_dir, internal.SITE_NAMELIST_DIR)
        if not site_namelist_dir.exists():
            os.makedirs(site_namelist_dir)

    if world:
        pass
