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
import sys
import datetime
import subprocess
sys.path.append("scripts")
from get_cable import GetCable
from build_cable import BuildCable
from run_cable_site import RunCable
from call_wrapper import benchmark_wrapper
from set_default_paths import set_paths

now = datetime.datetime.now()
date = now.strftime("%d_%m_%Y")
cwd = os.getcwd()
(sysname, nodename, release, version, machine) = os.uname()

#------------- User set stuff ------------- #
user = "mgk576"

#
## Repositories to test, default is head of the trunk against personal repo.
## But if trunk is false, repo1 could be anything
#
trunk = True
repo1 = "Trunk_%s" % (date)
repo2 = "CMIP6-MOSRS"
repos = [repo1, repo2]

#
## user directories ...
#
src_dir = "src"
run_dir = "runs"
log_dir = "logs"
plot_dir = "plots"
output_dir = "outputs"
restart_dir = "restart_files"
namelist_dir = "namelists"

#
## Needs different paths for NCI, storm ... this is set for my mac
## comment out the below and set your own, see scripts/set_default_paths.py
#
(met_dir, NCDIR, NCMOD, FC, CFLAGS, LD, LDFLAGS) = set_paths(nodename)

#
## Met files ...
#
if "unsw" in nodename:
    met_subset = ['AU-Tum_2002-2016_OzFlux_Flux.nc']
    #met_subset = [] # if empty...run all the files in the met_dir
else:
    met_subset = ['TumbaFluxnet.1.4_met.nc']
    #met_subset = [] # if empty...run all the files in the met_dir

#
## science configs
#
sci1 = {
        "cable_user%GS_SWITCH": "'medlyn'",
}

sci2 = {
        "cable_user%GS_SWITCH": "'leuning'",
}
sci_configs = [sci1, sci2]

#
## MPI stuff
#
mpi = False
num_cores = None #4 # set to a number, if None it will use all cores...!

# ------------------------------------------- #


benchmark_wrapper(user, trunk, repos, src_dir, run_dir, log_dir, met_dir,
                  plot_dir, output_dir, restart_dir, namelist_dir, NCDIR,
                  NCMOD, FC, CFLAGS, LD, LDFLAGS, sci_configs, mpi, num_cores,
                  met_subset, cwd)
