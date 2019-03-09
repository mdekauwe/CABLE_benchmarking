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
sys.path.append("scripts")
from get_cable import GetCable
from build_cable import BuildCable
from run_cable_site import RunCable
from call_wrapper import benchmark_wrapper

now = datetime.datetime.now()
date = now.strftime("%d_%m_%Y")
cwd = os.getcwd()
(sysname, nodename, release, version, machine) = os.uname()

#------------- User set stuff ------------- #
user = "mgk576"

repo1 = "Trunk_%s" % (date)
repo2 = "CMIP6-MOSRS"
repos = [repo1, repo2]

# user directories ...
src_dir = "src"
run_dir = "runs"
log_dir = "logs"
plot_dir = "plots"
met_dir = "/Users/mdekauwe/Desktop/plumber_met"
output_dir = "outputs"
restart_dir = "restart_files"
namelist_dir = "namelists"

# Needs different paths for NCI, storm ... this is set for my mac
if "Mac" in nodename:
    NCDIR = '/opt/local/lib/'
    NCMOD = '/opt/local/include/'
    FC = 'gfortran'
    CFLAGS = '-O2'
    LD = "'-lnetcdf -lnetcdff'"
    LDFLAGS = "'-L/opt/local/lib -O2'"
elif "unsw" in nodename:
    raise("not implemented!")
    #NCDIR = '/opt/local/lib/'
    #NCMOD = '/opt/local/include/'
    #FC = 'gfortran'
    #CFLAGS = '-O2'
    #LD = "'-lnetcdf -lnetcdff'"
    #LDFLAGS = "'-L/opt/local/lib -O2'"
elif "raijin" in nodename:
    raise("not implemented!")

# science configs
sci1 = {
        "cable_user%GS_SWITCH": "'medlyn'",
}

sci2 = {
        "cable_user%GS_SWITCH": "'leuning'",
}
sci_configs = [sci1, sci2]

mpi = False
num_cores = 4 # set to a number, if None it will use all cores...!
# if empty...run all the files in the met_dir
met_subset = ['TumbaFluxnet.1.4_met.nc']
#met_subset = []
# ------------------------------------------- #


benchmark_wrapper(user, repos, src_dir, run_dir, log_dir, met_dir, plot_dir,
                  output_dir, restart_dir, namelist_dir, NCDIR, NCMOD, FC,
                  CFLAGS, LD, LDFLAGS, sci_configs, mpi, num_cores, met_subset,
                  cwd)
