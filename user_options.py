import datetime
import os
import sys
import shutil

now = datetime.datetime.now()
date = now.strftime("%d_%m_%Y")
cwd = os.getcwd()
(sysname, nodename, release, version, machine) = os.uname()

sys.path.append("scripts")
from set_default_paths import set_paths


#------------- User set stuff ------------- #

#
## Qsub stuff ... ignore this block if not running a qsub script
#
project = "w35"
qsub_fname = "benchmark_cable_qsub.sh"
ncpus = 2
mem = "32GB"
wall_time = "01:30:00"
email_address = "mdekauwe@gmail.com"

#
## Repositories to test, default is head of the trunk against personal repo.
## But if trunk is false, repo1 could be anything
#
user = "mgk576"
trunk = True
#repo1 = "Trunk_%s" % (date)
repo1 = "Trunk"
#share_branch = False
#repo2 = "integration"
share_branch = True
repo2 = "test_jxs599"
repos = [repo1, repo2]


#
## user directories ...
#
src_dir = "src"
aux_dir = "src/CABLE-AUX"
run_dir = "runs"
log_dir = "logs"
plot_dir = "plots"
output_dir = "outputs"
restart_dir = "restart_files"
namelist_dir = "namelists"

if not os.path.exists(src_dir):
    os.makedirs(src_dir)

#
## Needs different paths for NCI, storm ... this is set for my mac
## comment out the below and set your own, see scripts/set_default_paths.py
#
(met_dir, NCDIR, NCMOD, FC, FCMPI, CFLAGS, LD, LDFLAGS) = set_paths(nodename)

#
## Met files ...
#
#met_subset = ['FI-Hyy_1996-2014_FLUXNET2015_Met.nc',\
#              'AU-Tum_2002-2017_OzFlux_Met.nc']
#met_subset = ['TumbaFluxnet.1.4_met.nc']

# Till fixed
#met_dir = "/g/data/w35/mgk576/research/CABLE_runs/met/Ozflux"
met_subset = ['AU-Tum_2002-2017_OzFlux_Met.nc','AU-How_2003-2017_OzFlux_Met.nc']
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

sci3 = {
        "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}

sci4 = {
        "cable_user%FWSOIL_SWITCH": "'standard'",
}

sci5 = {
        "cable_user%GS_SWITCH": "'medlyn'",
        "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}

sci6 = {
        "cable_user%GS_SWITCH": "'leuning'",
        "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}


sci7 = {
        "cable_user%GS_SWITCH": "'medlyn'",
        "cable_user%FWSOIL_SWITCH": "'standard'",
}

sci8 = {
        "cable_user%GS_SWITCH": "'leuning'",
        "cable_user%FWSOIL_SWITCH": "'standard'",
}


#sci_configs = [sci1, sci2, sci3, sci4, sci5, sci6, sci7, sci8]
sci_configs = [sci1, sci2]
#
## MPI stuff
#
mpi = True
num_cores = ncpus # set to a number, if None it will use all cores...!

# ----------------------------------------------------------------------- #
