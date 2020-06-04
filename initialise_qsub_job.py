#!/usr/bin/env python

"""
Checkout CABLE repositories, build executables and generate a qsub script to
wrap cable benchmarking scripts when used on raijin.

We can't use the run_comparison script as raijin nodes have no internet
connection.

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (12.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import datetime
import subprocess
from optparse import OptionParser

from user_options import *

sys.path.append("scripts")
from get_cable import GetCable
from build_cable import BuildCable
from generate_qsub_script import create_qsub_script

create_qsub_script(qsub_fname, ncpus, mem, wall_time, project, email_address)


parser = OptionParser()
parser.add_option("-s", "--skipsrc", action="store_true", default=False,
                  help="Rebuild src?")

(options, args) = parser.parse_args()

if options.skipsrc == False:

    #
    ## Get CABLE ...
    #
    G = GetCable(src_dir=src_dir, user=user)
    G.main(repo_name=repos[0], trunk=trunk) # Default is True
    G.main(repo_name=repos[1], trunk=False) # integration branch

    #
    ## Build CABLE ...
    #
    B = BuildCable(src_dir=src_dir, NCDIR=NCDIR, NCMOD=NCMOD, FC=FC,
                   CFLAGS=CFLAGS, LD=LD, LDFLAGS=LDFLAGS)
    B.main(repo_name=repos[0])
    B.main(repo_name=repos[1])
