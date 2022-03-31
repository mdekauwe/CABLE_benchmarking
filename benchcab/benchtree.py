from pathlib import Path
import os
class BenchTree():
    """Manage the directory tree to run the benchmarking for CABLE"""

    def __init__(self, curdir:Path):
        
        self.src_dir = curdir/"src"
        self.aux_dir = curdir/"src/CABLE-AUX"
        self.run_dir = curdir/"runs"
        self.log_dir = curdir/"logs"
        self.plot_dir = curdir/"plots"
        self.output_dir = curdir/"outputs"
        self.restart_dir = curdir/"restart_files"
        self.namelist_dir = curdir/"namelists"

    def create_minbenchtree(self):
        """Create the minimum directory tree needed to run the CABLE benchmarking.
        At least, we need:
           - a source directory to checkout and compile the repository branches
           - a run directory to run the testcases."""

        dir_to_create= [ 
            self.src_dir, 
            self.run_dir,
            ]
        for mydir in dir_to_create:
            if not Path.is_dir(mydir):
                os.makedirs(mydir)

