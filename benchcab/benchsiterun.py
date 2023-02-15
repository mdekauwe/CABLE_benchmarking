#!/usr/bin/env python

# To run the CABLE benchmarking at single sites
import argparse
import sys
import os
from pathlib import Path
import yaml

from benchcab.run_cable_site import RunCableSite
import benchcab.internal as internal
from benchcab.internal import validate_environment
from benchcab.bench_config import read_config

# Define names of default config files globally
default_config = "config.yaml"
default_science = "site_configs.yaml"


def myparse(arglist):
    """
    Parse arguments given as list (arglist)
    """
    parser = argparse.ArgumentParser(
        description="Run CABLE simulations at single sites for benchmarking"
    )
    parser.add_argument(
        "-q",
        "--qsub",
        help="Creates a qsub job script if running at NCI",
        action="store_true",
    )
    parser.add_argument(
        "-c", "--config", help="Config filename", default=default_config
    )
    parser.add_argument(
        "-s",
        "--science_config",
        help="Config file to define the various configurations to run",
        default=default_science,
    )

    args = parser.parse_args(arglist)

    (_, nodename, _, _, _) = os.uname()
    if args.qsub and not "nci" in nodename:
        print("Remote scripts are only implemented for NCI machine")
        print("You can not invoke benchsiterun -q if not running at NCI")
        raise

    if not "nci" in nodename and not args.met_dir:
        raise (
            "You need to specify the path to the meteorological data if you are not running at NCI."
        )

    return args


def read_sci_configs(sci_configfile):
    """Read the science config file"""

    with open(sci_configfile, "r") as fin:
        sci_configs = yaml.safe_load(fin)

    return sci_configs


def main(args):
    """To run CABLE on single sites for the benchmarking.
    Keyword arguments are the same as the command line arguments for the benchsiterun command
    """
    # TODO(Sean) need to perform checks as we cannot trust the
    # user to use `benchsiterun` correctly:
    # - validate directory structure (function to be implemented)
    # - build was successful and executables exist?

    config = read_config(args.config)

    validate_environment(project=config['project'], modules=config['modules'])

    # Read science configurations
    sci_configs = read_sci_configs(args.science_config)

    os.chdir(internal.CWD / internal.SITE_RUN_DIR)
    for branchid, b in enumerate(config['use_branches']):
        branch = config[b]

        # Define the name for the executable: cable for serial, cable-mpi for mpi runs
        cable_exe = f"cable{'-mpi'*internal.MPI}"

        R = RunCableSite(
            met_dir=internal.MET_DIR,
            log_dir=Path(internal.CWD / internal.SITE_LOG_DIR),
            output_dir=Path(internal.CWD / internal.SITE_OUTPUT_DIR),
            restart_dir=Path(internal.CWD / internal.SITE_RESTART_DIR),
            aux_dir=Path(internal.CWD / internal.CABLE_AUX_DIR),
            namelist_dir=Path(internal.CWD / internal.SITE_NAMELIST_DIR),
            met_subset=config["met_subset"],
            cable_src=Path(internal.CWD / internal.SRC_DIR / branch["name"]),
            num_cores=internal.NUM_CORES,
            cable_exe=cable_exe,
            multiprocess=internal.MULTIPROCESS,
        )

        for sci_id, sci_config in enumerate(sci_configs.values()):
            R.main(sci_config, branchid, sci_id)

        os.chdir(internal.CWD)


def main_parse_args(arglist):
    """
    Call main with list of arguments. Callable from tests
    """
    # Must return so that check command return value is passed back to calling routine
    # otherwise py.test will fail
    return main(myparse(arglist))


def main_argv():
    """
    Call main and pass command line arguments. This is required for setup.py entry_points
    """
    mess = main_parse_args(sys.argv[1:])


if __name__ == "__main__":

    main_argv()
