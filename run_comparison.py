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

now = datetime.datetime.now()
date = now.strftime("%d_%m_%Y")
cwd = os.getcwd()


#------------- User set stuff ------------- #
user = "mgk576"

repo1 = "Trunk_%s" % (date)
repo2 = "CMIP6-MOSRS"
repos = [repo1, repo2]

# user directories ...
src_dir = "src"
run_dir = "runs"
log_dir = "logs"
met_dir = "/Users/mdekauwe/research/CABLE_runs/met_data/plumber_met"
output_dir = "outputs"
restart_dir = "restart_files"
namelist_dir = "namelists"

# Needs different paths for NCI, storm ...
NCDIR = '/opt/local/lib/'
NCMOD = '/opt/local/include/'
FC = 'gfortran'
CFLAGS = '-O2'
LD = "'-lnetcdf -lnetcdff'"
LDFLAGS = "'-L/opt/local/lib -O2'"

# science configs
sci1 = {
        "cable_user%FWSOIL_SWITCH": "'Standard'",
        "cable_user%GS_SWITCH": "'medlyn'",
}

sci2 = {
        "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
        "cable_user%GS_SWITCH": "'medlyn'",
}
sci_configs = [sci1, sci2]

mpi = False
num_cores = 4 # set to a number, if None it will use all cores...!
# if empty...run all the files in the met_dir
met_subset = ['TumbaFluxnet.1.4_met.nc']
# ------------------------------------------- #



# Get CABLE ...
G = GetCable(src_dir=src_dir, user=user)
G.main(repo_name=repo1, trunk=True)
G.main(repo_name=repo2, trunk=False)


# Build CABLE ...
B = BuildCable(src_dir=src_dir, NCDIR=NCDIR, NCMOD=NCMOD, FC=FC,
               CFLAGS=CFLAGS, LD=LD, LDFLAGS=LDFLAGS)
B.main(repo_name=repo1)
B.main(repo_name=repo2)


# Run CABLE for each science config, for each repo
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

os.chdir(run_dir)

for repo_id, repo in enumerate(repos):
    aux_dir = "../src/CABLE-AUX/"
    cable_src = "../src/%s" % (repo)
    R = RunCable(met_dir=met_dir, log_dir=log_dir, output_dir=output_dir,
                 restart_dir=restart_dir, aux_dir=aux_dir,
                 namelist_dir=namelist_dir, met_subset=met_subset,
                 cable_src=cable_src, mpi=mpi, num_cores=num_cores)
    for sci_id, sci_config in enumerate(sci_configs):
        R.main(sci_config, repo_id, sci_id)

os.chdir(cwd)
