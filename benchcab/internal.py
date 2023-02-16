"""internal.py: define all runtime constants in a single file."""

import os
import sys
import grp
from pathlib import Path

_, NODENAME, _, _, _ = os.uname()

# DIRECTORY PATHS/STRUCTURE:

# Path to the user's current working directory
CWD = Path.cwd()

# Path to the user's home directory
HOME_DIR = Path(os.environ["HOME"])

# Relative path to directory containing CABLE source codes
SRC_DIR = Path("src")

# Relative path to run directory that stores CABLE runs
RUN_DIR = Path("runs")

# Relative path to core namelist files
NAMELIST_DIR = Path("namelists")

# Relative path to CABLE Auxiliary repository (for spatial runs)
CABLE_AUX_DIR = SRC_DIR / "CABLE-AUX"

# Relative path to root directory for CABLE site runs
SITE_RUN_DIR = RUN_DIR / "site"

# Relative path to directory that stores CABLE log files
SITE_LOG_DIR = SITE_RUN_DIR / "logs"

# Relative path to directory that stores CABLE output files
SITE_OUTPUT_DIR = SITE_RUN_DIR / "outputs"

# Relative path to directory that stores CABLE restart files
SITE_RESTART_DIR = SITE_RUN_DIR / "restart_files"

# Relative path to namelist files generated for all site runs
SITE_NAMELIST_DIR = SITE_RUN_DIR / "namelists"

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


def validate_environment(project: str, modules: list):
    '''Performs checks on current user environment'''

    if "gadi.nci" not in NODENAME:
        print("Error: benchcab is currently implemented only on Gadi")
        sys.exit(1)

    namelist_dir = Path(CWD / NAMELIST_DIR)
    if not namelist_dir.exists():
        print("Error: cannot find 'namelists' directory in current working directory")
        sys.exit(1)

    required_groups = [project, "ks32", "wd9", "hh5"]
    groups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
    if not set(required_groups).issubset(groups):
        print(
            "Error: user does not have the required group permissions.",
            "The required groups are:", ", ".join(required_groups)
        )
        sys.exit(1)

    sys.path.append("/opt/Modules/v4.3.0/init")
    from python import module  # pylint: disable=import-error, import-outside-toplevel
    for modname in modules:
        if not module("is-avail", modname):
            print(f"Error: module ({modname}) is not available.")
            sys.exit(1)
