#!/usr/bin/env python

"""
Set default paths on various machines...

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (09.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import subprocess
import datetime

def set_paths(nodename):

    if "Mac" in nodename or "imac" in nodename:
        NCDIR = '/opt/local/lib/'
        NCMOD = '/opt/local/include/'
        FC = 'gfortran'
        CFLAGS = '-O2'
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L/opt/local/lib -O2'"

        #
        ## Met paths ...
        #
        met_dir = "/Users/mdekauwe/Desktop/plumber_met"

    elif "unsw" in nodename:
        cmd = "module load netcdf/4.1.3-intel"
        error = subprocess.call(cmd, shell=True)
        if error is 1:
            raise("Error loading netcdf libs")

        NCDIR = '/share/apps/netcdf/intel/4.1.3/lib'
        NCMOD = '/share/apps/netcdf/intel/4.1.3/include'
        FC = 'ifort'
        CFLAGS = '-O2'
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L/opt/local/lib -O2'"

        #
        ## Met paths ...
        #
        #met_dir = ("/srv/ccrc/data04/z3509830/Fluxnet_data/"
        #           "All_flux_sites_processed/all_sites_no_duplicates/"
        #           "Nc_files/Met")
        met_dir = ("/srv/ccrc/data45/z3509830/CABLE_runs/Inputs/"
                   "PLUMBER_sites/met")
    else:

    # this won't work on qsub as the nodename isn't raijinX, it is r1997 (etc)
    #elif "raijin" in nodename:

        cmd = "module unload netcdf"
        error = subprocess.call(cmd, shell=True)
        if error is 1:
            raise("Error unloading netcdf libs")

        cmd = "module load netcdf/4.3.3.1"
        error = subprocess.call(cmd, shell=True)
        if error is 1:
            raise("Error loading netcdf libs")

        NCDIR = '/apps/netcdf/4.3.3.1/lib'
        NCMOD = '/apps/netcdf/4.3.3.1/include'
        FC = 'ifort'
        CFLAGS = '-O2'
        LD = "'-lnetcdf -lnetcdff'"
        LDFLAGS = "'-L/opt/local/lib -O2'"
        #
        ## Met paths ...
        #
        #met_dir = ("/g/data1/w35/Shared_data/Observations/Fluxnet_data/"
        #           "FLUXNET2015/Processed_data/Missing_10%_Gapfill_20%/Daily")
        met_dir = "/g/data1/w35/amu561/PLUMBER_sites"

    return (met_dir, NCDIR, NCMOD, FC, CFLAGS, LD, LDFLAGS)
