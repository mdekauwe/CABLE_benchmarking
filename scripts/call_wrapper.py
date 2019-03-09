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
import glob
import datetime
import numpy as np
sys.path.append("scripts")
from get_cable import GetCable
from build_cable import BuildCable
from run_cable_site import RunCable
from benchmark_seasonal_plot import main as seas_plot

def benchmark_wrapper(user, repos, src_dir, run_dir, log_dir, met_dir, plot_dir,
                      output_dir, restart_dir, namelist_dir, NCDIR, NCMOD, FC,
                      CFLAGS, LD, LDFLAGS, sci_configs, mpi, num_cores,
                      met_subset, cwd):

    #"""

    # Get CABLE ...
    G = GetCable(src_dir=src_dir, user=user)
    G.main(repo_name=repos[0], trunk=True)
    G.main(repo_name=repos[1], trunk=False)


    # Build CABLE ...
    B = BuildCable(src_dir=src_dir, NCDIR=NCDIR, NCMOD=NCMOD, FC=FC,
                   CFLAGS=CFLAGS, LD=LD, LDFLAGS=LDFLAGS)
    B.main(repo_name=repos[0])
    B.main(repo_name=repos[1])

    # Run CABLE for each science config, for each repo
    if not os.path.exists(run_dir):
        os.makedirs(run_dir)
    os.chdir(run_dir)

    for repo_id, repo in enumerate(repos):
        aux_dir = "../src/CABLE-AUX/"
        cable_src = "../src/%s" % (repo)
        for sci_id, sci_config in enumerate(sci_configs):
            R = RunCable(met_dir=met_dir, log_dir=log_dir,
                         output_dir=output_dir, restart_dir=restart_dir,
                         aux_dir=aux_dir, namelist_dir=namelist_dir,
                         met_subset=met_subset, cable_src=cable_src, mpi=mpi,
                         num_cores=num_cores)
            R.main(sci_config, repo_id, sci_id)
    #"""

    # Make seasonal plots ...
    ofdir = os.path.join(run_dir, output_dir)
    pldir = os.path.join(run_dir, plot_dir)
    all_files = glob.glob(os.path.join(ofdir, "*.nc"))
    sites = np.unique([os.path.basename(f).split(".")[0].split("_")[0] \
                       for f in all_files])

    for site in sites:
        for sci_id, sci_config in enumerate(sci_configs):
            fn1 = os.path.join(ofdir, "%s_R0_S%d_out.nc" % (site, sci_id))
            fn2 = os.path.join(ofdir, "%s_R1_S%d_out.nc" % (site, sci_id))
            plot_fname = "%s/%s_S%d_seas_plot.pdf" % (pldir, site, sci_id)
            seas_plot(fn1, fn2, plot_fname)

    os.chdir(cwd)
