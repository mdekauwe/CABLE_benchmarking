"""Contains the `Task` class definition."""

import os
import shutil
from pathlib import Path
import glob
import f90nml

from benchcab import internal


class Task:
    """A class used to represent a single fluxsite task."""

    def __init__(
        self,
        branch_name: str,
        met_forcing_file: str,
        sci_conf_key: str,
        sci_config: dict
    ) -> None:
        self.branch_name = branch_name
        self.met_forcing_file = met_forcing_file
        self.sci_conf_key = sci_conf_key
        self.sci_config = sci_config

    def get_task_name(self) -> str:
        """Returns the file name convention used for this task."""
        met_forcing_base_filename = self.met_forcing_file.split(".")[0]
        return f"{self.branch_name}_{met_forcing_base_filename}_{self.sci_conf_key}"

    def get_output_filename(self) -> str:
        """Returns the file name convention used for the netcdf output file."""
        return f"{self.get_task_name()}_out.nc"

    def get_log_filename(self) -> str:
        """Returns the file name convention used for the log file."""
        return f"{self.get_task_name()}_log.txt"

    def clean_task(self, root_dir=internal.CWD):
        """Cleans output files, namelist files, log files and cable executables if they exist."""

        task_name = self.get_task_name()
        task_dir = Path(root_dir, internal.SITE_TASKS_DIR, task_name)

        if Path.exists(task_dir / internal.CABLE_EXE):
            os.remove(task_dir / internal.CABLE_EXE)

        if Path.exists(task_dir / internal.CABLE_NML):
            os.remove(task_dir / internal.CABLE_NML)

        if Path.exists(task_dir / internal.CABLE_VEGETATION_NML):
            os.remove(task_dir / internal.CABLE_VEGETATION_NML)

        if Path.exists(task_dir / internal.CABLE_SOIL_NML):
            os.remove(task_dir / internal.CABLE_SOIL_NML)

        output_file = self.get_output_filename()
        if Path.exists(root_dir / internal.SITE_OUTPUT_DIR / output_file):
            os.remove(root_dir / internal.SITE_OUTPUT_DIR / output_file)

        log_file = self.get_log_filename()
        if Path.exists(root_dir / internal.SITE_LOG_DIR / log_file):
            os.remove(root_dir / internal.SITE_LOG_DIR / log_file)

        return self

    def fetch_files(self, root_dir=internal.CWD):
        """Retrieves all files necessary to run cable in the task directory.

        Namely:
        - Copies contents of 'namelists' directory to 'runs/site/tasks/<task_name>' directory:
        - Copies cable executable from source directory:
        """

        task_dir = Path(root_dir, internal.SITE_TASKS_DIR, self.get_task_name())
        shutil.copytree(root_dir / internal.NAMELIST_DIR, task_dir, dirs_exist_ok=True)
        shutil.copy(
            root_dir / internal.SRC_DIR / self.branch_name / "offline" / internal.CABLE_EXE,
            task_dir / internal.CABLE_EXE
        )

        return self

    def adjust_namelist_file(self, root_dir=internal.CWD):
        """Make necessary adjustments to the CABLE namelist file."""

        task_dir = Path(root_dir, internal.SITE_TASKS_DIR, self.get_task_name())

        patch_nml = {
            "cable": {
                "filename": {
                    "met": self.met_forcing_file,
                    "out": self.get_output_filename(),
                    "log": self.get_log_filename(),
                    "restart_out": " ",
                    "type": internal.CWD / internal.GRID_FILE,
                    "veg": internal.CWD / internal.VEG_FILE,
                    "soil": internal.CWD / internal.SOIL_FILE,
                },
                "output": {
                    "restart": False,
                },
                "fixedCO2": internal.CABLE_FIXED_CO2_CONC,
                "casafile": {
                    "phen": internal.CWD / internal.PHEN_FILE,
                    "cnpbiome": internal.CWD / internal.CNPBIOME_FILE,
                },
                "spinup": ".FALSE.",
            }
        }

        # TODO(Sean) the science config dictionary must comply with the f90nml api
        patch_nml["cable"].update(self.sci_config)

        f90nml.patch(task_dir / internal.CABLE_NML, patch_nml)

        return self

    def setup_task(self):
        """Does all file manipulations to run cable in the task directory.

        These include:
        1. cleaning output, namelist, log files and cable executables if they exist
        2. copying namelist files (cable.nml, pft_params.nml and cable_soil_parm.nml)
        into the `runs/site/tasks/<task_name>` directory.
        3. copying the cable executable from the source directory
        4. make appropriate adjustments to namelist files
        """

        self.clean_task() \
            .fetch_files() \
            .adjust_namelist_file()


def get_fluxnet_tasks(config: dict, science_config: dict) -> list[Task]:
    """Returns a list of fluxnet tasks to run."""
    branch_names = [config[branch_alias]["name"] for branch_alias in config["use_branches"]]
    met_sites = get_all_met_sites() if config["met_subset"] == [] else config["met_subset"]
    tasks = [
        Task(branch_name, site, key, science_config[key])
        for branch_name in branch_names for site in met_sites for key in science_config
    ]
    return tasks


def get_all_met_sites():
    """Get list of all met files in `MET_DIR` directory."""
    return glob.glob(os.path.join(internal.MET_DIR, "*.nc"))
