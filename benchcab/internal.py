"""internal.py: define all runtime constants in a single file."""

import os
import sys
from pathlib import Path

_, NODENAME, _, _, _ = os.uname()
if "gadi.nci" not in NODENAME:
    print("Error: benchcab is currently implemented only on Gadi")
    sys.exit(1)

# Path to met files:
MET_DIR = Path("/g/data/ks32/CLEX_Data/PLUMBER2/v1-0/Met/")

# Parameters for job script:
QSUB_FNAME = "benchmark_cable_qsub.sh"
NCPUS = 18
MEM = "30GB"
WALL_TIME = "6:00:00"
MPI = False
MULTIPROCESS = True
NUM_CORES = NCPUS  # set to a number, if None it will use all cores...!
