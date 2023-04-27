"""Contains functions for job script creation and submission on Gadi."""

import os
import sys
import subprocess
from pathlib import Path

from benchcab.internal import QSUB_FNAME, NCPUS, MEM, WALL_TIME


def create_job_script(
    project: str,
    user: str,
    config_path: str,
    modules: list
):
    """Creates a job script for executing `benchsiterun` on Gadi."""

    email_address = f"{user}@nci.org.au"

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

    with open(QSUB_FNAME, "w", encoding="utf-8") as file:
        file.write("#!/bin/bash\n")
        file.write("\n")
        file.write("#PBS -l wd\n")
        file.write(f"#PBS -l ncpus={NCPUS}\n")
        file.write(f"#PBS -l mem={MEM}\n")
        file.write(f"#PBS -l walltime={WALL_TIME}\n")
        file.write("#PBS -q normal\n")
        file.write(f"#PBS -P {project}\n")
        file.write("#PBS -j oe\n")
        file.write(f"#PBS -M {email_address}\n")
        file.write("#PBS -l storage=gdata/ks32+gdata/wd9+gdata/hh5"
                   f"+gdata/{project}+{curdir_root}/{curdir_proj}\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("module purge\n")
        file.write("module use /g/data/hh5/public/modules\n")
        file.write("module load conda/analysis3-unstable\n")
        for module_name in modules:
            file.write(f"module add {module_name}\n")
        file.write(f"benchcab fluxnet-run-tasks --no-submit --config={config_path}")
        file.write("\n")

    os.chmod(QSUB_FNAME, 0o755)


def submit_job():
    """Submits the job script specified by `QSUB_FNAME`."""

    cmd = f"qsub {QSUB_FNAME}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print("Error when submitting job to NCI queue")
        print(proc.stderr)
        sys.exit(1)

    print(f"Benchmark submitted in PBS job: {proc.stdout}")
