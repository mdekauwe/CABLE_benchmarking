#!/usr/bin/env python

"""
Set default paths on various machines...

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (06.06.2020)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import subprocess
from pathlib import Path


def set_paths(nodename, envfile=""):

    print(Path.cwd())
    assert Path(envfile).is_file(), f"Environment file {envfile} is not found."

    if "Mac" in nodename or "imac" in nodename:
        NCDIR = "/opt/local/lib/"
        NCMOD = "/opt/local/include/"
        FC = "gfortran"
        FCMPI = "gfortran-mp-9"
        CFLAGS = "-O2"
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L/opt/local/lib -O2'"

        #
        ## Met paths ...
        #
        met_dir = "/Users/mdekauwe/research/plumber_test"

    elif "unsw" in nodename:
        cmd = "module load netcdf-c/4.4.1.1-intel"
        cmd = "module load netcdf-f/4.4.4-intel"
        error = subprocess.call(cmd, shell=True)
        if error == 1:
            raise ("Error loading netcdf libs")

        NCDIR = "/share/apps/netcdf-f/intel/4.4.4/lib"
        NCMOD = "/share/apps/netcdf-f/intel/4.4.4/include"

        FC = "ifort"
        FCMPI = "mpif90"
        CFLAGS = "-O2"
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L/opt/local/lib -O2'"

        #
        ## Met paths ...
        met_dir = (
            "/srv/ccrc/data04/z3509830/Fluxnet_data/"
            "All_flux_sites_processed_PLUMBER2/"
            "Post-processed_PLUMBER2_outputs/Nc_files/Met"
        )

    elif "gadi" in nodename:
        # Load modules
        MODULESHOME = Path(os.environ["MODULESHOME"])
        sys.path.append(str(MODULESHOME / "init"))
        import python as mod

        with Path(envfile).open() as rfile:
            ModToLoad = rfile.readlines()

        mod.module("purge")
        for modname in ModToLoad:
            mod.module("load", modname.rstrip())

        # Setup variables for compilation
        # FC is setup by the modules
        NCBASE = Path(os.environ["NETCDF"])  # Set when loading the netcdf module
        NCDIR = NCBASE / "lib"
        NCMOD = NCBASE / "include"
        FCMPI = "mpif90"
        FC = os.environ["FC"]
        CFLAGS = "-O2"
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L'$NCDIR' -O0'"
        met_dir = Path(
            "/g/data/w97/W35_GDATA_MOVED/Shared_data/Observations/Fluxnet_data/"
            "Post-processed_PLUMBER2_outputs/Nc_files/Met"
        )

    else:
        raise("Machine unknown. This case needs to be defined in set_default_paths.")

    compilation_opt={
        "met_dir":met_dir,
        "NCDIR": NCDIR,
        "NCMOD": NCMOD,
        "FC": FC,
        "FCMPI": FCMPI,
        "CFLAGS": CFLAGS,
        "LD":LD,
        "LDFLAGS":LDFLAGS,
    }
    return compilation_opt
