#!/usr/bin/env python

"""Contains the main program entry point for `benchsiterun`.

Runs the CABLE test suite for single sites on a Gadi compute node.
"""

import argparse
import sys
from multiprocessing import cpu_count, Process

import numpy as np

from benchcab.run_cable_site import run_tasks
from benchcab import internal
from benchcab.internal import validate_environment, DEFAULT_CONFIG, DEFAULT_SCIENCE
from benchcab.task import get_fluxnet_tasks
from benchcab.bench_config import read_config, read_science_config


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
    sci_configs = read_science_config(args.science_config)

    validate_environment(project=config['project'], modules=config['modules'])

    tasks = get_fluxnet_tasks(config, sci_configs)

    if internal.MULTIPROCESS:
        num_cores = cpu_count() if internal.NUM_CORES is None else internal.NUM_CORES
        chunk_size = int(np.ceil(len(tasks) / num_cores))

        jobs = []
        for i in range(num_cores):
            start = chunk_size * i
            end = min(chunk_size * (i + 1), len(tasks))

            # setup a list of processes that we want to run
            proc = Process(target=run_tasks, args=[tasks[start:end]])
            proc.start()
            jobs.append(proc)

        # wait for all multiprocessing processes to finish
        for j in jobs:
            j.join()

    else:
        run_tasks(tasks)


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
