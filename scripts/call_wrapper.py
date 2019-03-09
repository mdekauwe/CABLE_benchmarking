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

def benchmark_wrapper(user, repos, src_dir, run_dir, log_dir, met_dir,
                      output_dir, restart_dir, namelist_dir, NCDIR, NCMOD, FC,
                      CFLAGS, LD, LDFLAGS, sci_configs, mpi, num_cores,
                      met_subset, cwd):

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

    os.chdir(cwd)
