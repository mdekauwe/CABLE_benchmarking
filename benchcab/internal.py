"""internal.py: define all runtime constants in a single file."""

import os
import sys
from pathlib import Path

# TODO(Sean) it is bad to include error checking in global file

_, NODENAME, _, _, _ = os.uname()

# DIRECTORY PATHS/STRUCTURE:

# Path to the user's current working directory
CWD = Path.cwd()

# Path to the user's home directory
HOME_DIR = Path(os.environ["HOME"])

# Path to directory containing CABLE source codes
SRC_DIR = CWD / "src"

# TODO(Sean) what does CABLE auxiliary do?
CABLE_AUX_DIR = SRC_DIR / "CABLE-AUX"

# Path to run directory that stores CABLE runs
RUN_DIR = CWD / "runs"

# Path to root directory for CABLE site runs
SITE_RUN_DIR = RUN_DIR / "site"

# Path to directory that stores CABLE log files
SITE_LOG_DIR = SITE_RUN_DIR / "logs"

# Path to directory that stores CABLE output files
SITE_OUTPUT_DIR = SITE_RUN_DIR / "outputs"

# Path to directory that stores CABLE restart files
SITE_RESTART_DIR = SITE_RUN_DIR / "restart_files"

# TODO(Sean) add a comment
SITE_NAMELIST_DIR = SITE_RUN_DIR / "namelists"

# Path to namelist files in bench_example
# TODO(Sean) add better comment
NAMELIST_DIR = CWD / "namelists"

# Path to met files:
MET_DIR = Path("/g/data/ks32/CLEX_Data/PLUMBER2/v1-0/Met/")

# CABLE SVN root url:
CABLE_SVN_ROOT = "https://trac.nci.org.au/svn/cable"

# Parameters for job script:
QSUB_FNAME = "benchmark_cable_qsub.sh"
NCPUS = 18
MEM = "30GB"
WALL_TIME = "6:00:00"
MPI = False
MULTIPROCESS = True
NUM_CORES = NCPUS  # set to a number, if None it will use all cores...!


def validate_environment():
    '''Performs checks on current user environment'''

    if "gadi.nci" not in NODENAME:
        print("Error: benchcab is currently implemented only on Gadi")
        sys.exit(1)

    if not NAMELIST_DIR.exists():
        print("Error: cannot find 'namelists' directory in current working directory")
        sys.exit(1)
