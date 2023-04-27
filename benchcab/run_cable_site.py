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
from multiprocessing import cpu_count, Process
import netCDF4
import numpy as np

from benchcab.get_cable import svn_info_show_item
from benchcab.internal import (
    CWD,
    SRC_DIR,
    SITE_TASKS_DIR,
    SITE_OUTPUT_DIR,
    CABLE_EXE,
    CABLE_NML,
    NUM_CORES
)
from benchcab.task import Task


def run_tasks_in_parallel(tasks: list[Task]):
    """Runs tasks in parallel by scattering tasks across multiple processes."""

    num_cores = cpu_count() if NUM_CORES is None else NUM_CORES
    chunk_size = int(np.ceil(len(tasks) / num_cores))

    jobs = []
    for i in range(num_cores):
        start = chunk_size * i
        end = min(chunk_size * (i + 1), len(tasks))

        # setup a list of processes that we want to run
        proc = Process(target=run_tasks, args=[tasks[start:end]])
        proc.start()
        jobs.append(proc)

    # wait for all multiprocessing processes to finish
    for j in jobs:
        j.join()


def run_tasks(tasks: list[Task], verbose=False):
    """Executes CABLE for each task in `tasks`."""

    for task in tasks:
        task_name = task.get_task_name()
        os.chdir(CWD / SITE_TASKS_DIR / task_name)
        cmd = f"./{CABLE_EXE} {CABLE_NML}"
        if not verbose:
            cmd += " > /dev/null 2>&1"
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as err:
            print("Job failed to submit: ", err.cmd)

        add_attributes_to_output_file(
            output_file=Path(CWD / SITE_OUTPUT_DIR / f"{task_name}_out.nc"),
            nml_file=Path(CWD / SITE_TASKS_DIR / task_name / CABLE_NML),
            sci_config=task.sci_config,
            url=svn_info_show_item(CWD / SRC_DIR / task.branch_name, "url"),
            rev=svn_info_show_item(CWD / SRC_DIR / task.branch_name, "revision"),
        )

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
