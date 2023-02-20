"""Contains the `Task` class definition."""

import os
import shutil
from pathlib import Path
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

    def setup_task(self):
        """Does all file manipulations to run cable in the task directory.

        These include:
        1. cleaning output, namelist, log files and cable executables if they exist
        2. copying namelist files (cable.nml, pft_params.nml and cable_soil_parm.nml)
        into the `runs/site/tasks/<task_name>` directory.
        3. copying the cable executable from the source directory
        4. make appropriate adjustments to namelist files
        """

        task_name = self.get_task_name()
        task_dir = Path(internal.CWD, internal.SITE_TASKS_DIR, task_name)

        # Clean output, namelist, log files and cable executables if they exist

        if Path.exists(task_dir / internal.CABLE_EXE):
            os.remove(task_dir / internal.CABLE_EXE)

        if Path.exists(task_dir / internal.CABLE_NML):
            os.remove(task_dir / internal.CABLE_NML)

        if Path.exists(task_dir / internal.CABLE_VEGETATION_NML):
            os.remove(task_dir / internal.CABLE_VEGETATION_NML)

        if Path.exists(task_dir / internal.CABLE_SOIL_NML):
            os.remove(task_dir / internal.CABLE_SOIL_NML)

        output_file = f"{task_name}_out.nc"
        if Path.exists(internal.CWD / internal.SITE_OUTPUT_DIR / output_file):
            os.remove(internal.CWD / internal.SITE_OUTPUT_DIR / output_file)

        log_file = f"{task_name}_log.txt"
        if Path.exists(internal.CWD / internal.SITE_LOG_DIR / log_file):
            os.remove(internal.CWD / internal.SITE_LOG_DIR / log_file)

        # Copy contents of 'namelists' directory to 'runs/site/tasks/<task_name>' directory:

        shutil.copytree(internal.CWD / internal.NAMELIST_DIR, task_dir, dirs_exist_ok=True)

        # Copy cable executable from source directory:

        shutil.copy(
            internal.CWD / internal.SRC_DIR / self.branch_name / "offline" / internal.CABLE_EXE,
            task_dir / internal.CABLE_EXE
        )

        # Make appropriate adjustments to namelist files:

        patch_nml = {
            "cable": {
                "filename": {
                    "met": self.met_forcing_file,
                    "out": output_file,
                    "log": log_file,
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
        patch_nml.update(self.sci_config)

        f90nml.patch(task_dir / internal.CABLE_NML, patch_nml)
