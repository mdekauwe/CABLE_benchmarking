"""Contains functions for generating the directory structure used for `benchcab`."""
from pathlib import Path
import os
import shutil

from benchcab import internal
from benchcab.task import Task


def clean_directory_tree():
    """Remove pre-existing directories in current working directory."""
    src_dir = Path(internal.CWD, internal.SRC_DIR)
    if src_dir.exists():
        shutil.rmtree(src_dir)

    run_dir = Path(internal.CWD, internal.RUN_DIR)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def setup_src_dir():
    """Make `src` directory."""

    src_dir = Path(internal.CWD, internal.SRC_DIR)
    if not src_dir.exists():
        print(f"Creating {src_dir.relative_to(internal.CWD)} directory: {src_dir}")
        os.makedirs(src_dir)


def setup_fluxnet_directory_tree(fluxnet_tasks: list[Task], verbose=False):
    """Generate the directory structure used of `benchcab`."""

    run_dir = Path(internal.CWD, internal.RUN_DIR)
    if not run_dir.exists():
        os.makedirs(run_dir)

    site_run_dir = Path(internal.CWD, internal.SITE_RUN_DIR)
    if not site_run_dir.exists():
        os.makedirs(site_run_dir)

    site_log_dir = Path(internal.CWD, internal.SITE_LOG_DIR)
    if not site_log_dir.exists():
        print(
            f"Creating {site_log_dir.relative_to(internal.CWD)} directory: {site_log_dir}"
        )
        os.makedirs(site_log_dir)

    site_output_dir = Path(internal.CWD, internal.SITE_OUTPUT_DIR)
    if not site_output_dir.exists():
        print(
            f"Creating {site_output_dir.relative_to(internal.CWD)} directory: {site_output_dir}"
        )
        os.makedirs(site_output_dir)

    site_tasks_dir = Path(internal.CWD, internal.SITE_TASKS_DIR)
    if not site_tasks_dir.exists():
        print(
            f"Creating {site_tasks_dir.relative_to(internal.CWD)} directory: {site_tasks_dir}"
        )
        os.makedirs(site_tasks_dir)

    site_analysis_dir = Path(internal.CWD, internal.SITE_ANALYSIS_DIR)
    if not site_analysis_dir.exists():
        print(
            f"Creating {site_analysis_dir.relative_to(internal.CWD)} directory: {site_analysis_dir}"
        )
        os.makedirs(site_analysis_dir)

    site_bitwise_cmp_dir = Path(internal.CWD, internal.SITE_BITWISE_CMP_DIR)
    if not site_bitwise_cmp_dir.exists():
        print(
            f"Creating {site_bitwise_cmp_dir.relative_to(internal.CWD)} directory: "
            f"{site_bitwise_cmp_dir}"
        )
        os.makedirs(site_bitwise_cmp_dir)

    print("Creating task directories...")
    for task in fluxnet_tasks:
        task_dir = Path(internal.CWD, internal.SITE_TASKS_DIR, task.get_task_name())
        if not task_dir.exists():
            if verbose:
                print(f"Creating {task_dir.relative_to(internal.CWD)}: " f"{task_dir}")
            os.makedirs(task_dir)
