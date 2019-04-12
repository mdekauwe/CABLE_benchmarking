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
ncpus = 16
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
repo2 = "integration"
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

if not os.path.exists(src_dir):
    os.makedirs(src_dir)

#
## Needs different paths for NCI, storm ... this is set for my mac
## comment out the below and set your own, see scripts/set_default_paths.py
#
(met_dir, NCDIR, NCMOD, FC, CFLAGS, LD, LDFLAGS) = set_paths(nodename)

#
## Met files ...
#
#met_subset = ['TumbaFluxnet.1.4_met.nc']
met_subset = [] # if empty...run all the files in the met_dir

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


sci_configs = [sci1, sci2, sci3, sci4, sci5, sci6, sci7, sci8]

#
## MPI stuff
#
mpi = True
num_cores = ncpus #4 # set to a number, if None it will use all cores...!

# ----------------------------------------------------------------------- #
