#!/usr/bin/env python

"""
Run CABLE either for a single site, a subset, or all the flux sites pointed to
in the met directory

- Only intended for biophysics
- Set mpi = True if doing a number of flux sites

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (16.06.2020)"
__email__ = "mdekauwe@gmail.com"

import os
import subprocess
from pathlib import Path
import multiprocessing
import queue
import netCDF4

from benchcab.get_cable import svn_info_show_item
from benchcab.internal import (
    CWD,
    SRC_DIR,
    SITE_TASKS_DIR,
    SITE_OUTPUT_DIR,
    CABLE_EXE,
    CABLE_NML,
    CABLE_STDOUT_FILENAME,
    NUM_CORES,
)
from benchcab.task import Task


def run_tasks(tasks: list[Task], verbose=False):
    """Runs tasks in `tasks` serially."""
    for task in tasks:
        run_task(task, verbose=verbose)


def run_tasks_in_parallel(tasks: list[Task], verbose=False):
    """Runs tasks in `tasks` in parallel across multiple processes."""

    task_queue: multiprocessing.Queue = multiprocessing.Queue()
    for task in tasks:
        task_queue.put(task)

    processes = []
    num_cores = multiprocessing.cpu_count() if NUM_CORES is None else NUM_CORES
    for _ in range(num_cores):
        proc = multiprocessing.Process(target=worker, args=[task_queue, verbose])
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()


def worker(task_queue: multiprocessing.Queue, verbose=False):
    """Runs tasks in `task_queue` until the queue is emptied."""
    while True:
        try:
            task = task_queue.get_nowait()
        except queue.Empty:
            return
        run_task(task, verbose=verbose)


def run_task(task: Task, verbose=False):
    """Run the CABLE executable for the given task."""
    task_name = task.get_task_name()
    task_dir = CWD / SITE_TASKS_DIR / task_name
    if verbose:
        print(
            f"Running task {task_name}... CABLE standard output "
            f"saved in {task_dir / CABLE_STDOUT_FILENAME}"
        )

    if verbose:
        print(f"  cd {task_dir}")
    os.chdir(task_dir)

    cmd = f"./{CABLE_EXE} {CABLE_NML} > {CABLE_STDOUT_FILENAME} 2>&1"
    try:
        if verbose:
            print(f"  {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Error: CABLE returned an error for task {task_name}")
        return

    output_file = CWD / SITE_OUTPUT_DIR / task.get_output_filename()
    if verbose:
        print(f"  Adding attributes to output file: {output_file}")
    add_attributes_to_output_file(
        output_file=output_file,
        nml_file=Path(CWD / SITE_TASKS_DIR / task_name / CABLE_NML),
        sci_config=task.sci_config,
        url=svn_info_show_item(CWD / SRC_DIR / task.branch_name, "url"),
        rev=svn_info_show_item(CWD / SRC_DIR / task.branch_name, "revision"),
    )

    if verbose:
        print(f"  cd {CWD}")
    os.chdir(CWD)


def add_attributes_to_output_file(output_file, nml_file, sci_config, url, rev):
    """Adds global attributes to netcdf output file.

    Attributes include branch url, branch revision number and key value pairs in
    the namelist file used to run cable.
    """

    # TODO(Sean) remove science configurations as these are in the namelist file

    nc_output = netCDF4.Dataset(output_file, "r+")

    # Add SVN info to output file
    nc_output.setncattr("cable_branch", url)
    nc_output.setncattr("svn_revision_number", rev)

    # Add science configurations to output file
    for key, value in sci_config.items():
        nc_output.setncattr("SCI_CONFIG", f"{key}_{value}")

    # Add namelist to output file
    with open(nml_file, "r", encoding="utf-8") as file:
        namelist = file.readlines()
    for line in namelist:
        if line.strip() == "":
            # skip blank lines
            continue
        if line.strip().startswith("!"):
            # skip lines that are comments
            continue
        if line.startswith("&"):
            # skip start of namelist
            continue
        if "=" not in line:
            # skip lines without key = value statement
            continue
        key = str(line.strip().split("=")[0]).rstrip()
        val = str(line.strip().split("=")[1]).rstrip()
        nc_output.setncattr(key, val)

    nc_output.close()
