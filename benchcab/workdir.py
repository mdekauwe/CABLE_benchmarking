"""A module containing functions for generating the directory structure used for `benchcab`."""

from pathlib import Path
import os
import shutil
from typing import Union

from benchcab import internal
from benchcab.fluxsite import Task


def clean_directory_tree(root_dir=internal.CWD):
    """Remove pre-existing directories in current working directory."""
    src_dir = Path(root_dir, internal.SRC_DIR)
    if src_dir.exists():
        shutil.rmtree(src_dir)

    run_dir = Path(root_dir, internal.RUN_DIR)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def setup_src_dir(root_dir=internal.CWD):
    """Make `src` directory."""

    src_dir = Path(root_dir, internal.SRC_DIR)
    if not src_dir.exists():
        print(f"Creating {src_dir.relative_to(root_dir)} directory: {src_dir}")
        os.makedirs(src_dir)


def fluxsite_directory_tree_list(fluxsite_tasks: list[Task], root_dir=internal.CWD) -> set:
    """Generate a list of all the work directories used for fluxsite tests"""

    # Create the list of directories as sets because the order is not important
    # and we want to avoid duplications.
    fluxsite_paths = []

    # Run directory
    fluxsite_paths.append(Path(root_dir, internal.RUN_DIR))

    # Fluxsite run directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_RUN_DIR))

    # Fluxsite log directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_LOG_DIR))

    # Fluxsite output directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_OUTPUT_DIR))

    # Fluxsite tasks directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_TASKS_DIR))

    # Fluxsite analysis directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_ANALYSIS_DIR))

    # Fluxsite bit-wise comparison directory
    fluxsite_paths.append(Path(root_dir, internal.FLUXSITE_BITWISE_CMP_DIR))

    # Fluxsite tasks directories. append all of them as a set().
    task_paths = []
    for task in fluxsite_tasks:
        task_paths.append(
            Path(root_dir, internal.FLUXSITE_TASKS_DIR, task.get_task_name()))
    fluxsite_paths.append(task_paths)

    return fluxsite_paths


def setup_fluxsite_directory_tree(
    fluxsite_paths: list[Union[Path, list]], root_dir=internal.CWD, verbose=False
):
    """Generate the directory structure used by `benchcab`."""

    for work_path in fluxsite_paths:
        if isinstance(work_path, list):
            print("Creating task directories...")

            for task_dir in work_path:
                if verbose:
                    print(f"Creating {task_dir.relative_to(root_dir)}: {task_dir}")
                task_dir.mkdir(parents=True, exist_ok=True)
        else:
            print(
                f"Creating {work_path.relative_to(root_dir)} directory: {work_path}"
            )
            work_path.mkdir(parents=True, exist_ok=True)
