#!/usr/bin/env python

"""
Get CABLE, build the executables, setup the run directory, run CABLE ... this is
a wrapper around the actual scripts (see scripts directory)

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (09.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import shutil
import sys
import datetime
import subprocess

from user_options import *

sys.path.append("scripts")
from call_wrapper import benchmark_wrapper


if __name__ == "__main__":

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--qsub", action="store_true", default=False,
                      help="Run qsub script?")

    (options, args) = parser.parse_args()

    main(options.old_fname, options.new_fname, options.plot_fname)

    if option.qsub:
        benchmark_wrapper_qsub(repos, run_dir, log_dir, met_dir, plot_dir,
                               output_dir, restart_dir, namelist_dir,
                               sci_configs, mpi, num_cores, met_subset, cwd)
    else:
        benchmark_wrapper(user, trunk, repos, src_dir, run_dir, log_dir,
                          met_dir, plot_dir, output_dir, restart_dir,
                          namelist_dir, NCDIR, NCMOD, FC, CFLAGS, LD, LDFLAGS,
                          sci_configs, mpi, num_cores, met_subset, cwd)
