"""internal.py: define all runtime constants in a single file."""

import os
import sys
import grp
from pathlib import Path

_, NODENAME, _, _, _ = os.uname()

# Default config file names
DEFAULT_CONFIG = "config.yaml"

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

# CABLE standard output filename
CABLE_STDOUT_FILENAME = "out.txt"

# Contains the default science configurations used to run the CABLE test suite
# (when a science config file is not provided by the user)
DEFAULT_SCIENCE_CONFIGURATIONS = {
    "sci0": {"cable": {"cable_user": {"GS_SWITCH": "medlyn"}}},
    "sci1": {"cable": {"cable_user": {"GS_SWITCH": "leuning"}}},
    "sci2": {"cable": {"cable_user": {"FWSOIL_SWITCH": "Haverd2013"}}},
    "sci3": {"cable": {"cable_user": {"FWSOIL_SWITCH": "standard"}}},
    "sci4": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    "sci5": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    "sci6": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
    "sci7": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
}

# Contains the site ids for each met forcing file associated with an experiment
# on modelevaluation.org
MEORG_EXPERIMENTS = {
    # List of site ids associated with the 'Five site test'
    # experiment (workspace: NRI Land testing), see:
    # https://modelevaluation.org/experiment/display/xNZx2hSvn4PMKAa9R
    "five-site-test": [
        "AU-Tum",
        "AU-How",
        "FI-Hyy",
        "US-Var",
        "US-Whs",
    ],
    # List of site ids associated with the 'Forty two site test'
    # experiment (workspace: NRI Land testing), see:
    # https://modelevaluation.org/experiment/display/urTKSXEsojdvEPwdR
    "forty-two-site-test": [
        "AU-Tum",
        "AU-How",
        "AU-Cum",
        "AU-ASM",
        "AU-GWW",
        "AU-Ctr",
        "AU-Stp",
        "BR-Sa3",
        "CA-Qfo",
        "CH-Dav",
        "CN-Cha",
        "CN-Din",
        "DE-Geb",
        "DE-Gri",
        "DE-Hai",
        "DE-Tha",
        "DK-Sor",
        "FI-Hyy",
        "FR-Gri",
        "FR-Pue",
        "GF-Guy",
        "IT-Lav",
        "IT-MBo",
        "IT-Noe",
        "NL-Loo",
        "RU-Fyo",
        "US-Blo",
        "US-GLE",
        "US-Ha1",
        "US-Me2",
        "US-MMS",
        "US-Myb",
        "US-NR1",
        "US-PFa",
        "US-FPe",
        "US-SRM",
        "US-SRG",
        "US-Ton",
        "US-UMB",
        "US-Var",
        "US-Whs",
        "US-Wkg",
    ]
}


def get_met_sites(experiment: str) -> list[str]:
    '''Get a list of met forcing file basenames specified by an experiment

    The `experiment` argument either specifies a key in `MEORG_EXPERIMENTS` or a site id
    within the five-site-test experiment.

    Assume all site ids map uniquely to a met file in MET_DIR.
    '''

    if experiment in MEORG_EXPERIMENTS["five-site-test"]:
        # the user is specifying a single met site
        return [next(MET_DIR.glob(f"{experiment}*")).name]

    met_sites = [
        next(MET_DIR.glob(f"{site_id}*")).name
        for site_id in MEORG_EXPERIMENTS[experiment]
    ]

    return met_sites


def validate_environment(project: str, modules: list):
    '''Performs checks on current user environment'''

    if "gadi.nci" not in NODENAME:
        print("Error: benchcab is currently implemented only on Gadi")
        sys.exit(1)

    namelist_dir = Path(CWD / NAMELIST_DIR)
    if not namelist_dir.exists():
        print("Error: cannot find 'namelists' directory in current working directory")
        sys.exit(1)

    required_groups = [project, "ks32", "hh5"]
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

    all_site_ids = set(
        MEORG_EXPERIMENTS["five-site-test"] +
        MEORG_EXPERIMENTS["forty-two-site-test"]
    )
    for site_id in all_site_ids:
        paths = list(MET_DIR.glob(f"{site_id}*"))
        if not paths:
            print(f"Error: failed to infer met file for site id '{site_id}' in {MET_DIR}.")
            sys.exit(1)
        if len(paths) > 1:
            print(f"Error: multiple paths infered for site id: '{site_id}' in {MET_DIR}.")
            sys.exit(1)
