#!/usr/bin/env python

import argparse
import sys
from pathlib import Path
import os
import shlex
import subprocess

from benchcab.bench_config import BenchSetup
from benchcab.benchtree import BenchTree
from benchcab.build_cable import BuildCable
from benchcab.get_cable import GetCable

# Site runs
from benchcab.run_cable_site import RunCableSite
from benchcab.setup.cases_fluxsites import *
from benchcab.setup.pbs_fluxsites import qsub_fname
import benchcab.benchsiterun as benchsiterun


def parse_args(arglist):
    """
    Parse arguments given as list (arglist)
    """
    parser = argparse.ArgumentParser(description="Run the benchmarking for CABLE")
    parser.add_argument("-c","--config", help="Config filename", default="config.yaml")
    parser.add_argument("-s", "--science_config", help="Config file to define the various configurations to run", default="site_configs.yaml")
    parser.add_argument("-f","--fluxnet", help="Runs the tests for the Fluxnet sites only", action="store_true")
    parser.add_argument("-w","--world", help="Runs the global tests only",action="store_true")
    parser.add_argument("-b","--bitrepro", help="Check bit reproducibility, not implemented yet",action="store_true")
    parser.add_argument("-r", "--rebuild", action="store_true", default=False, help="Rebuild src?")

    args = parser.parse_args(arglist)

    if args.bitrepro:
        print("Bit reproducibility not implemented yet")
        sys.exit()
    
    if args.fluxnet and args.world:
        print("You can not specify -f and -g together.")
        print("To run all the tests, do not specify any of those 2 options.")
        sys.exit()

    return args

def retrieve_cable_code(benchdirs:BenchTree, opt:dict):
    """Checkout the 2 branches of CABLE from the svn repository in the 
    source directory created at setup.
    benchdir: BenchTree, contains path information for paths in the working directory
    opt: dict, contains the branch information we want to use"""

    # Aliases to branches to use:
    branch_alias = opt["use_branches"]
    branch1 = opt[branch_alias[0]]
    branch2 = opt[branch_alias[1]]

    G = GetCable(src_dir=benchdirs.src_dir, user=opt["user"])
    G.main(**branch1)
    G.main(**branch2)

def build_cable_code(benchdirs:BenchTree, compilation_opt:dict, opt:dict, mpi:False):

    # Aliases to branches to use:
    branch_alias = opt["use_branches"]
    branch1 = opt[branch_alias[0]]
    branch2 = opt[branch_alias[1]]

    B = BuildCable(
        src_dir=benchdirs.src_dir,
        ModToLoad=opt["modules"],
        NCDIR=compilation_opt["NCDIR"],
        NCMOD=compilation_opt["NCMOD"],
        FC=compilation_opt["FC"],
        CFLAGS=compilation_opt["CFLAGS"],
        LD=compilation_opt["LD"],
        LDFLAGS=compilation_opt["LDFLAGS"],
        mpi=mpi,
        )
    B.main(repo_name=branch1["name"])
    B.main(repo_name=branch2["name"])

def setup_site_runs(opt, compilation_opt, benchdirs, sci_configs, mpi, multiprocess):
    """Ssetup specific to site simulations"""

    # Aliases to branches to use:
    branch_alias = opt["use_branches"]
    run_branches=[opt[branch_alias[0]],]
    run_branches.append(opt[branch_alias[1]])

    start_dir=Path.cwd()
    os.chdir(benchdirs.runroot_dir/"site")
    for branchid, branch in enumerate(run_branches):
        branch_name = branch["name"]
        cable_src = benchdirs.src_dir/branch_name

        # Define the name for the executable: cable for serial, cable-mpi for mpi runs
        cable_exe = f"cable{'-mpi'*mpi}"

        R = RunCableSite(
            met_dir=compilation_opt["met_dir"],
            log_dir=benchdirs.site_run["log_dir"],
            output_dir=benchdirs.site_run["output_dir"],
            restart_dir=benchdirs.site_run["restart_dir"],
            aux_dir=benchdirs.aux_dir,
            namelist_dir=benchdirs.site_run["namelist_dir"],
            met_subset=[],
            cable_src=cable_src,
            num_cores=None,
            cable_exe=cable_exe,
            multiprocess=multiprocess,
        )

        for sci_id, sci_config in enumerate(sci_configs.values()):
            R.main(sci_config, branchid, sci_id)

    os.chdir(start_dir)


def main(args):

    # Setup of the benchmark:
    #------------------------
    # - read config file.
    # - define compilation variables.
    # - create minimal work directory tree.
    # - checkout the CABLE source codes.
    # - compile the CABLE source codes.

    mysetup = BenchSetup(args.config)
    opt, compilation_opt, benchdirs = mysetup.setup_bench()

    # Get the source code for both branches
    print("Retrieving the source code from both branches in the src/ directory")
    retrieve_cable_code(benchdirs, opt)


    # Run the benchmark:
    # We run both at single sites and spatial runs unless otherwise specified
    # by command line arguments
    #------------------------------------------------------------------------
    # Identify cases to run
    run_flux    = not args.world
    run_spatial = not args.fluxnet

    mess=""
    if run_flux:
        mess=mess+"Running the single sites tests "
        print("Running the single sites tests ")

        mpi = False
        multiprocess = True

        # Build the source codes
        build_cable_code(benchdirs, compilation_opt, opt, mpi)

        # Create directory tree for site runs
        benchdirs.create_sitebenchtree()
        
        # Create the qsub script for NCI if needed
        (_, nodename, _, _, _) = os.uname()
        if "nci" in nodename:
            benchsiterun.main(qsub=True, config=args.config, science_config=args.science_config)

            cmd = shlex.split(f"qsub {qsub_fname}")
            sb=subprocess.run(cmd, capture_output=True)
            if (sb.returncode != 0):
                print("Error when submitting job to NCI queue")
                print(sb.stderr)
                sys.exit(1)
            else:
                print(f"Benchmark submitted in PBS job: {sb.stdout}")
        
        else:
            print("Only running on NCI is implemented at the moment.")

    if run_spatial:
        mess=mess+"Running the spatial tests "
        print("Running the spatial tests ")

    return mess

def main_parse_args(arglist):
    """
    Call main with list of arguments. Callable from tests
    """
    # Must return so that check command return value is passed back to calling routine
    # otherwise py.test will fail
    return main(parse_args(arglist))

def main_argv():
    """
    Call main and pass command line arguments. This is required for setup.py entry_points
    """
    mess = main_parse_args(sys.argv[1:])

if __name__ == "__main__":

    main_argv()