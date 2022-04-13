from pathlib import Path
import os
class BenchTree(object):
    """Manage the directory tree to run the benchmarking for CABLE"""

    def __init__(self, curdir:Path):
        
        self.src_dir = curdir/"src"
        self.aux_dir = curdir/"src/CABLE-AUX"
        self.plot_dir = curdir/"plots"
        # Run directory and its sub-directories
        self.runroot_dir = curdir/"runs"
        self.site_run = {
            "log_dir": self.runroot_dir/"site/logs",
            "output_dir": self.runroot_dir/"site/outputs",
            "restart_dir": self.runroot_dir/"site/restart_files",
            "namelist_dir": self.runroot_dir/"site/namelists",
        }

    def create_minbenchtree(self):
        """Create the minimum directory tree needed to run the CABLE benchmarking.
        At least, we need:
           - a source directory to checkout and compile the repository branches
           - a run directory to run the testcases."""

        dir_to_create= [ 
            self.src_dir, 
            self.runroot_dir,
            ]
        for mydir in dir_to_create:
            if not Path.is_dir(mydir):
                os.makedirs(mydir)

    def create_sitebenchtree(self):
        """Create directory tree for site benchmark"""

        # Make sure the default directories are created
        self.create_minbenchtree()

        # Create the sub-directories in the run directory
        for mydir in self.site_run.values():
            if not mydir.is_dir():
                os.makedirs(mydir)
    
