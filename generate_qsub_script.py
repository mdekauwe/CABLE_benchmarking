#!/usr/bin/env python

"""
Generate a qsub script to wrap cable benchmarking scripts when used on raijin


That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (11.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import datetime
import subprocess

def create_qsub_script(ofname, ncpus, mem, wall_time, project, email_address):

    f = open(ofname, "w")

    f.write("#!/bin/bash\n")
    f.write("\n")
    f.write("#PBS -l wd\n")
    f.write("#PBS -l ncpus=%d\n" % (ncpus))
    f.write("#PBS -l mem=%s\n" % (mem))
    f.write("#PBS -l walltime=%s\n" % (wall_time))
    f.write("#PBS -q normal\n")
    f.write("#PBS -P %s\n" % (project))
    f.write("#PBS -m ae\n")
    f.write("#PBS -M %s\n" % (email_address))
    f.write("set -e\n")
    f.write("\n")
    f.write("ulimit -s unlimited")
    f.write("\n")
    f.write("cd $PBS_O_WORKDIR\n")
    f.write("\n")
    f.write("umask 022\n")
    f.write("\n")
    f.write("python ./run_comparison.py\n")
    f.write("\n")

    f.close()

    os.chmod(ofname, 0o755)



#------------- User set stuff ------------- #
project = "w35"
ofname = "run_comparison_on_nci.sh"
ncpus = 2
mem = "32GB"
wall_time = "00:30:00"
email_address = "mdekauwe@gmail.com"
# ------------------------------------------- #

create_qsub_script(ofname, ncpus, mem, wall_time, project, email_address)
