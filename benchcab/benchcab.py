#!/usr/bin/env python

"""Contains the main program entry point for `benchcab`."""

import argparse
import sys
import shutil

from benchcab.job_script import create_job_script, submit_job
from benchcab.bench_config import read_config
from benchcab.benchtree import setup_directory_tree
from benchcab.build_cable import build_cable_offline
from benchcab.get_cable import checkout_cable, checkout_cable_auxiliary, archive_rev_number
from benchcab.internal import validate_environment, CWD, NAMELIST_DIR, SITE_RUN_DIR


def parse_args(arglist):
    """Parse arguments given by `arglist`."""

    parser = argparse.ArgumentParser(description="Run the benchmarking for CABLE")
    parser.add_argument(
        "-c",
        "--config",
        help="Config filename",
        default="config.yaml"
    )
    parser.add_argument(
        "-s",
        "--science_config",
        help="Config file to define the various configurations to run",
        default="site_configs.yaml"
    )
    parser.add_argument(
        "-f",
        "--fluxnet",
        help="Runs the tests for the Fluxnet sites only",
        action="store_true"
    )
    parser.add_argument(
        "-w",
        "--world",
        help="Runs the global tests only",
        action="store_true"
    )
    parser.add_argument(
        "-b",
        "--bitrepro",
        help="Check bit reproducibility, not implemented yet",
        action="store_true"
    )
    parser.add_argument(
        "-r",
        "--rebuild",
        action="store_true",
        default=False,
        help="Rebuild src?"
    )

    args = parser.parse_args(arglist)

    if args.bitrepro:
        print("Bit reproducibility not implemented yet")
        sys.exit()

    if args.fluxnet and args.world:
        print("You can not specify -f and -g together.")
        print("To run all the tests, do not specify any of those 2 options.")
        sys.exit()

    return args


def main(args):
    """Main program entry point for `benchcab`."""

    config = read_config(args.config)

    validate_environment(project=config['project'], modules=config['modules'])

    # TODO(Sean) add command line argument 'clean' or 'new' to remove existing directories
    setup_directory_tree(fluxnet=args.fluxnet, world=args.world)

    for branch_alias in config['use_branches']:
        checkout_cable(branch_config=config[branch_alias], user=config['user'])
    checkout_cable_auxiliary()
    archive_rev_number()

    if args.fluxnet:
        print("Running the single sites tests ")

        # TODO(Sean) why?
        # Copy contents of 'namelists' directory to 'runs/site' directory:
        shutil.copytree(CWD / NAMELIST_DIR, CWD / SITE_RUN_DIR, dirs_exist_ok=True)

        # TODO(Sean) A single function that does all the file manipulations of copying and
        # moving files would be ideal so that the job simply goes into a directory and
        # executes cable. Most of the code in run_cable_site.py is manipulating files to
        # setup for running cable. These file manipulations can be moved benchcab.

        for branch_alias in config['use_branches']:
            branch = config[branch_alias]
            build_cable_offline(branch['name'], config['modules'])

        create_job_script(
            project=config['project'],
            user=config['user'],
            config_path=args.config,
            sci_config_path=args.science_config,
            modules=config['modules']
        )

        submit_job()

    if args.world:
        print("Running the spatial tests ")
        print("Warning: spatial tests not yet implemented")


def main_parse_args(arglist):
    """Call main with list of arguments. Callable from tests."""
    # Must return so that check command return value is passed back to calling routine
    # otherwise py.test will fail
    return main(parse_args(arglist))


def main_argv():
    """Call main and pass command line arguments.

    This is required for setup.py entry_points
    """
    main_parse_args(sys.argv[1:])


if __name__ == "__main__":

    main_argv()
