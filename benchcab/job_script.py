import os
import sys
import shlex
import subprocess
from pathlib import Path

from benchcab.internal import QSUB_FNAME, NCPUS, MEM, WALL_TIME


def create_job_script(project: str, user: str, config_path: str, sci_config_path: str):
    email_address = f"{user}@nci.org.au"

    # Add the local directory to the storage flag for PBS
    # TODO(Sean) why?
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

    f = open(QSUB_FNAME, "w")

    f.write("#!/bin/bash\n")
    f.write("\n")
    f.write("#PBS -l wd\n")
    f.write("#PBS -l ncpus=%d\n" % (NCPUS))
    f.write("#PBS -l mem=%s\n" % (MEM))
    f.write("#PBS -l walltime=%s\n" % (WALL_TIME))
    f.write("#PBS -q normal\n")
    f.write("#PBS -P %s\n" % (project))
    f.write("#PBS -j oe\n")
    f.write("#PBS -M %s\n" % (email_address))
    f.write(
        f"#PBS -l storage=gdata/ks32+gdata/wd9+gdata/hh5+gdata/{project}+{curdir_root}/{curdir_proj}\n"
    )
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("module purge\n")
    # TODO(Sean) we should load the modules specified by user config file?
    f.write("module use /g/data/hh5/public/modules\n")
    f.write("module load conda/analysis3-unstable\n")
    f.write("module add netcdf/4.7.1\n")
    f.write(f"benchsiterun --config={config_path} --science_config={sci_config_path}\n")
    f.write("\n")

    f.close()

    os.chmod(QSUB_FNAME, 0o755)


def submit_job():
    cmd = shlex.split(f"qsub {QSUB_FNAME}")
    sb = subprocess.run(cmd, capture_output=True)
    if sb.returncode != 0:
        print("Error when submitting job to NCI queue")
        print(sb.stderr)
        sys.exit(1)

    print(f"Benchmark submitted in PBS job: {sb.stdout}")
