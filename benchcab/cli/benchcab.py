#!/usr/bin/env python

import argparse
import sys

def parse_args(arglist):
    """
    Parse arguments given as list (arglist)
    """
    parser = argparse.ArgumentParser(description="Run the benchmarking for CABLE")
    parser.add_argument("-c","--config", help="Config filename", default="config.yaml")
    parser.add_argument("-f","--fluxnet", help="Runs the tests for the Fluxnet sites only", action="store_true")
    parser.add_argument("-s","--spatial", help="Runs the spatial tests only",action="store_true")
    parser.add_argument("-b","--bitrepro", help="Check bit reproducibility, not implemented yet",action="store_true")

    args = parser.parse_args(arglist)

    if args.bitrepro:
        print("Bit reproducibility not implemented yet")
        sys.exit()

    return args

def main(args):

    # Identify cases to run
    run_flux    = not args.spatial
    run_spatial = not args.fluxnet

    mess=""
    if run_flux:
        mess=mess+"Running the single sites tests "
        print("Running the single sites tests ")

    if run_spatial:
        mess=mess+"Running the spatial tests "
        print("Running the spatial tests ")

    return mess

def main_parse_args(arglist):
    """
    Call main with list of arguments. Callable from tests
    """
    # Must return so that check command return value is passed back to calling routine
    # otherwise py.test will fail
    return main(parse_args(arglist))

def main_argv():
    """
    Call main and pass command line arguments. This is required for setup.py entry_points
    """
    mess = main_parse_args(sys.argv[1:])

if __name__ == "__main__":

    main_argv()