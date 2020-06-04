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
import glob
import datetime
import subprocess
import numpy as np
from optparse import OptionParser


from user_options import *

sys.path.append("scripts")
from get_cable import GetCable
from build_cable import BuildCable
from run_cable_site import RunCable


parser = OptionParser()
parser.add_option("--qsub", action="store_true", default=False,
                  help="Run qsub script?")
parser.add_option("-s", "--skipsrc", action="store_true", default=False,
                  help="Rebuild src?")

(options, args) = parser.parse_args()

if options.qsub == False and options.skipsrc == False:

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


#
## Run CABLE for each science config, for each repo
#

if not os.path.exists(run_dir):
    os.makedirs(run_dir)
os.chdir(run_dir)

cable_aux = os.path.join("../", aux_dir)
for repo_id, repo in enumerate(repos):
    cable_src = os.path.join(os.path.join("../", src_dir), repo)
    for sci_id, sci_config in enumerate(sci_configs):
        R = RunCable(met_dir=met_dir, log_dir=log_dir,
                     output_dir=output_dir, restart_dir=restart_dir,
                     aux_dir=cable_aux, namelist_dir=namelist_dir,
                     met_subset=met_subset, cable_src=cable_src, mpi=mpi,
                     num_cores=num_cores)
        R.main(sci_config, repo_id, sci_id)


os.chdir(cwd)



### NOT INTEGRATED BUT WE NEED THE BELOW

#------------- Change stuff ------------- #
tmp_ancillary_dir = "global_files" # GSWP3 grid/mask file, temporarily

met_dir = "/g/data/wd9/MetForcing/Global/GSWP3_2017/"
run_start_yr = 1901
run_end_yr = 1901
walltime = "0:30:00"
qsub_fname = "qsub_wrapper_script_simulation.sh"

(log_fname, out_fname, restart_in_fname,
 restart_out_fname, year, co2_conc,
 nml_fname, spin_up, adjust_nml, sort_restarts) = cmd_line_parser()

C = RunCable(met_dir=met_dir, log_dir=log_dir, output_dir=output_dir,
             restart_dir=restart_dir, aux_dir=aux_dir, spin_up=spin_up,
             cable_src=cable_src, qsub_fname=qsub_fname, met_data=met_data,
             nml_fname=nml_fname, walltime=walltime,
             tmp_ancillary_dir=tmp_ancillary_dir)

# Setup initial namelist file and submit qsub job
if adjust_nml == False:
    C.initialise_stuff()
    C.setup_nml_file()
    C.run_qsub_script(start_yr, end_yr)

# qsub script is adjusting namelist file, i.e. for a different year
else:
    C.create_new_nml_file(log_fname, out_fname, restart_in_fname,
                          restart_out_fname, year, co2_conc)
