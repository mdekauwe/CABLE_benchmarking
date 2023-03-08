"""internal.py: define all runtime constants in a single file."""

import os
import sys
import grp
from pathlib import Path

_, NODENAME, _, _, _ = os.uname()

# Default config file names
DEFAULT_CONFIG = "config.yaml"
DEFAULT_SCIENCE = "site_configs.yaml"

# Parameters for job script:
QSUB_FNAME = "benchmark_cable_qsub.sh"
NCPUS = 18
MEM = "30GB"
WALL_TIME = "6:00:00"
MPI = False
MULTIPROCESS = True
NUM_CORES = NCPUS  # set to a number, if None it will use all cores...!

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

# Relative path to CABLE Auxiliary repository
CABLE_AUX_DIR = SRC_DIR / "CABLE-AUX"

# Relative path to CABLE grid info file
GRID_FILE = CABLE_AUX_DIR / "offline" / "gridinfo_CSIRO_1x1.nc"

# Relative path to modis_phenology_csiro.txt
PHEN_FILE = CABLE_AUX_DIR / "core" / "biogeochem" / "modis_phenology_csiro.txt"

# Relative path to pftlookup_csiro_v16_17tiles.csv
CNPBIOME_FILE = CABLE_AUX_DIR / "core" / "biogeochem" / "pftlookup_csiro_v16_17tiles.csv"

# Relative path to root directory for CABLE site runs
SITE_RUN_DIR = RUN_DIR / "site"

# Relative path to directory that stores CABLE log files
SITE_LOG_DIR = SITE_RUN_DIR / "logs"

# Relative path to directory that stores CABLE output files
SITE_OUTPUT_DIR = SITE_RUN_DIR / "outputs"

# Relative path to tasks directory where cable executables are run from
SITE_TASKS_DIR = SITE_RUN_DIR / "tasks"

# Path to met files:
MET_DIR = Path("/g/data/ks32/CLEX_Data/PLUMBER2/v1-0/Met/")

# CABLE SVN root url:
CABLE_SVN_ROOT = "https://trac.nci.org.au/svn/cable"

# CABLE executable file name:
CABLE_EXE = "cable-mpi" if MPI else "cable"

# CABLE namelist file name:
CABLE_NML = "cable.nml"

# CABLE vegetation namelist file:
CABLE_VEGETATION_NML = "pft_params.nml"

# CABLE soil namelist file:
CABLE_SOIL_NML = "cable_soilparm.nml"

# CABLE fixed C02 concentration
CABLE_FIXED_CO2_CONC = 400.0

# List of the 20 met forcing files associated with the CABLE_multisite_PLUMBER
# experiment on modelevaluation.org, see:
# https://modelevaluation.org/experiment/display/XMdi5K4zJpTe2S8aM
MEORG_PLUMBER_MET_FILES = [
    "AU-How_2003-2017_OzFlux_Met.nc",       # AU-How - PLUMBER
    "AU-Tum_2002-2017_OzFlux_Met.nc",       # AU-Tum - PLUMBER
    "BW-Ma1_2000-2000_LaThuile_Met.nc",     # BW-Ma1 - PLUMBER
    # "CA-Mer - PLUMBER",                   # CA-Mer - PLUMBER
    "ES-ES1_1999-2006_LaThuile_Met.nc",     # ES-ES1 - PLUMBER
    "ES-ES2_2005-2006_LaThuile_Met.nc",     # ES-ES2 - PLUMBER
    "FI-Hyy_1996-2014_FLUXNET2015_Met.nc",  # FI-Hyy - PLUMBER
    "FR-Hes_1997-2006_LaThuile_Met.nc",     # FR-Hes - PLUMBER
    "HU-Bug_2003-2006_LaThuile_Met.nc",     # HU-Bug - PLUMBER
    "ID-Pag_2002-2003_LaThuile_Met.nc",     # ID-Pag - PLUMBER
    "IT-Amp_2003-2006_LaThuile_Met.nc",     # IT-Amp - PLUMBER
    "NL-Loo_1997-2013_FLUXNET2015_Met.nc",  # NL-Loo - PLUMBER
    "PT-Esp_2002-2004_LaThuile_Met.nc",     # PT-Esp - PLUMBER
    "US-Blo_2000-2006_FLUXNET2015_Met.nc",  # US-Blo - PLUMBER
    "US-FPe_2000-2006_LaThuile_Met.nc",     # US-FPe - PLUMBER
    "US-Ha1_1992-2012_FLUXNET2015_Met.nc",  # US-Ha1 - PLUMBER
    "US-Ho1_1996-2004_LaThuile_Met.nc",     # US-Ho1 - PLUMBER
    "US-Syv_2002-2008_FLUXNET2015_Met.nc",  # US-Syv - PLUMBER
    "US-UMB_2000-2014_FLUXNET2015_Met.nc",  # US-UMB - PLUMBER
    "ZA-Kru_2000-2002_FLUXNET2015_Met.nc",  # ZA-Kru - PLUMBER
]


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

    for met_file_name in MEORG_PLUMBER_MET_FILES:
        met_file_path = Path(MET_DIR, met_file_name)
        if not met_file_path.exists():
            print(f"Error: cannot find met file {met_file_path}")
            sys.exit(1)
