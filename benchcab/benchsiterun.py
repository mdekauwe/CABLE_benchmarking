#!/usr/bin/env python

"""Contains the main program entry point for `benchsiterun`."""

# To run the CABLE benchmarking at single sites
import argparse
import sys
import os
from pathlib import Path

from benchcab.run_cable_site import RunCableSite
from benchcab import internal
from benchcab.internal import validate_environment
from benchcab.bench_config import read_config, read_science_config

# Define names of default config files globally
DEFAULT_CONFIG = "config.yaml"
DEFAULT_SCIENCE = "site_configs.yaml"


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
        "-c", "--config", help="Config filename", default=DEFAULT_CONFIG
    )
    parser.add_argument(
        "-s",
        "--science_config",
        help="Config file to define the various configurations to run",
        default=DEFAULT_SCIENCE,
    )

    args = parser.parse_args(arglist)

    return args


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
    sci_configs = read_science_config(args.science_config)

    os.chdir(internal.CWD / internal.SITE_RUN_DIR)
    for branchid, branch_alias in enumerate(config['use_branches']):
        branch = config[branch_alias]

        # Define the name for the executable: cable for serial, cable-mpi for mpi runs
        cable_exe = f"cable{'-mpi'*internal.MPI}"

        run_obj = RunCableSite(
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
            run_obj.main(sci_config, branchid, sci_id)

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
    main_parse_args(sys.argv[1:])


if __name__ == "__main__":

    main_argv()
