"""Contains functions for job script creation and submission on Gadi."""

import os
import sys
import subprocess
from pathlib import Path

from benchcab.internal import QSUB_FNAME, NCPUS, MEM, WALL_TIME


def create_job_script(
    project: str, user: str, config_path: str, modules: list, verbose=False
):
    """Creates a job script for executing `benchsiterun` on Gadi."""

    email_address = f"{user}@nci.org.au"
    module_load_lines = "\n".join(
        f"module add {module_name}" for module_name in modules
    )
    verbose_flag = "-v" if verbose else ""

    # Add the local directory to the storage flag for PBS
    curdir = Path.cwd().parts
    if "scratch" in curdir:
        curdir_root = "scratch"
        curdir_proj = curdir[2]
    elif "g" in curdir and "data" in curdir:
        curdir_root = "gdata"
        curdir_proj = curdir[3]
    else:
        print("Current directory structure unknown on Gadi")
        sys.exit(1)

    print(
        f"Creating PBS job script to run FLUXNET tasks on compute nodes: {QSUB_FNAME}"
    )
    with open(QSUB_FNAME, "w", encoding="utf-8") as file:
        file.write(
            f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={NCPUS}
#PBS -l mem={MEM}
#PBS -l walltime={WALL_TIME}
#PBS -q normal
#PBS -P {project}
#PBS -j oe
#PBS -M {email_address}
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/{project}+{curdir_root}/{curdir_proj}

module purge
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
{module_load_lines}

benchcab fluxnet-run-tasks --no-submit --config={config_path} {verbose_flag}
"""
        )

    os.chmod(QSUB_FNAME, 0o755)


def submit_job():
    """Submits the job script specified by `QSUB_FNAME`."""

    cmd = f"qsub {QSUB_FNAME}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print("Error when submitting job to NCI queue")
        print(proc.stderr)
        sys.exit(1)

    print(f"PBS job submitted: {proc.stdout.strip()}")
