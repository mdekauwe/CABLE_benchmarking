"""Contains the `Task` class definition."""

import os
import shutil
from pathlib import Path
from typing import TypeVar, Dict, Any
import f90nml

from benchcab import internal

# fmt: off
# pylint: disable=invalid-name,missing-function-docstring,line-too-long
# ======================================================
# Copyright (c) 2017 - 2022 Samuel Colvin and other contributors
# from https://github.com/pydantic/pydantic/blob/fd2991fe6a73819b48c906e3c3274e8e47d0f761/pydantic/utils.py#L200

KeyType = TypeVar('KeyType')


def deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping

# ======================================================
# pylint: enable=invalid-name,missing-function-docstring,line-too-long
# fmt: on


class Task:
    """A class used to represent a single fluxsite task."""

    def __init__(
        self,
        branch_id: int,
        branch_name: str,
        branch_patch: dict,
        met_forcing_file: str,
        sci_conf_id: int,
        sci_config: dict,
    ) -> None:
        self.branch_id = branch_id
        self.branch_name = branch_name
        self.branch_patch = branch_patch
        self.met_forcing_file = met_forcing_file
        self.sci_conf_id = sci_conf_id
        self.sci_config = sci_config

    def get_task_name(self) -> str:
        """Returns the file name convention used for this task."""
        met_forcing_base_filename = self.met_forcing_file.split(".")[0]
        return f"{met_forcing_base_filename}_R{self.branch_id}_S{self.sci_conf_id}"

    def get_output_filename(self) -> str:
        """Returns the file name convention used for the netcdf output file."""
        return f"{self.get_task_name()}_out.nc"

    def get_log_filename(self) -> str:
        """Returns the file name convention used for the log file."""
        return f"{self.get_task_name()}_log.txt"

    def clean_task(self, root_dir=internal.CWD, verbose=False):
        """Cleans output files, namelist files, log files and cable executables if they exist."""

        if verbose:
            print("  Cleaning task")

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

    def fetch_files(self, root_dir=internal.CWD, verbose=False):
        """Retrieves all files necessary to run cable in the task directory.

        Namely:
        - copies contents of 'namelists' directory to 'runs/site/tasks/<task_name>' directory.
        - copies cable executable from source to 'runs/site/tasks/<task_name>' directory.
        """

        task_dir = Path(root_dir, internal.SITE_TASKS_DIR, self.get_task_name())

        if verbose:
            print(
                f"  Copying namelist files from {root_dir / internal.NAMELIST_DIR} "
                f"to {task_dir}"
            )

        shutil.copytree(root_dir / internal.NAMELIST_DIR, task_dir, dirs_exist_ok=True)

        exe_src = (
            root_dir
            / internal.SRC_DIR
            / self.branch_name
            / "offline"
            / internal.CABLE_EXE
        )
        exe_dest = task_dir / internal.CABLE_EXE

        if verbose:
            print(f"  Copying CABLE executable from {exe_src} to {exe_dest}")

        shutil.copy(exe_src, exe_dest)

        return self

    def adjust_namelist_file(self, root_dir=internal.CWD, verbose=False):
        """Sets the base settings in the CABLE namelist file for this task."""

        patch_nml = {
            "cable": {
                "filename": {
                    "met": str(internal.MET_DIR / self.met_forcing_file),
                    "out": str(
                        root_dir / internal.SITE_OUTPUT_DIR / self.get_output_filename()
                    ),
                    "log": str(
                        root_dir / internal.SITE_LOG_DIR / self.get_log_filename()
                    ),
                    "restart_out": " ",
                    "type": str(root_dir / internal.GRID_FILE),
                },
                "output": {
                    "restart": False,
                },
                "fixedCO2": internal.CABLE_FIXED_CO2_CONC,
                "casafile": {
                    "phen": str(root_dir / internal.PHEN_FILE),
                    "cnpbiome": str(root_dir / internal.CNPBIOME_FILE),
                },
                "spinup": False,
            }
        }

        patch_nml = deep_update(patch_nml, self.sci_config)

        if verbose:
            # remove new line as we prepend the next message in patch_namelist_file()
            print("  Adjusting namelist file: ", end="")

        self.patch_namelist_file(patch_nml, root_dir=root_dir, verbose=verbose)

        return self

    def patch_namelist_file(self, patch: dict, root_dir=internal.CWD, verbose=False):
        """Writes a patch to the CABLE namelist file for this task.

        The `patch` dictionary must comply with the `f90nml` api.
        """

        task_dir = Path(root_dir, internal.SITE_TASKS_DIR, self.get_task_name())

        if verbose:
            # this message should not indent and start as lower case as we are
            # appending to the previous message
            print(
                f"applying patch to CABLE namelist file {task_dir / internal.CABLE_NML}"
            )

        cable_nml = f90nml.read(str(task_dir / internal.CABLE_NML))
        # remove namelist file as f90nml cannot write to an existing file
        os.remove(str(task_dir / internal.CABLE_NML))

        f90nml.write(deep_update(cable_nml, patch), str(task_dir / internal.CABLE_NML))

        return self

    def setup_task(self, root_dir=internal.CWD, verbose=False):
        """Does all file manipulations to run cable in the task directory.

        These include:
        1. cleaning output, namelist, log files and cable executables if they exist
        2. copying namelist files (cable.nml, pft_params.nml and cable_soil_parm.nml)
        into the `runs/site/tasks/<task_name>` directory.
        3. copying the cable executable from the source directory
        4. make appropriate adjustments to namelist files
        5. apply a branch patch if specified
        """

        if verbose:
            print(f"Setting up task: {self.get_task_name()}")

        self.clean_task(root_dir=root_dir, verbose=verbose)
        self.fetch_files(root_dir=root_dir, verbose=verbose)
        self.adjust_namelist_file(root_dir=root_dir, verbose=verbose)

        if self.branch_patch:
            if verbose:
                # remove new line as we prepend the next message in patch_namelist_file()
                print("  Adding branch specific namelist settings: ", end="")
            self.patch_namelist_file(
                self.branch_patch, root_dir=root_dir, verbose=verbose
            )


def get_fluxnet_tasks(
    realisations: list[dict], science_configurations: list[dict], met_sites: list[str]
) -> list[Task]:
    """Returns a list of fluxnet tasks to run."""
    # TODO(Sean) convert this to a generator
    tasks = [
        Task(
            branch_id=branch_id,
            branch_name=branch["name"],
            branch_patch=branch["patch"],
            met_forcing_file=site,
            sci_conf_id=sci_conf_id,
            sci_config=sci_config,
        )
        for branch_id, branch in enumerate(realisations)
        for site in met_sites
        for sci_conf_id, sci_config in enumerate(science_configurations)
    ]
    return tasks


def get_fluxnet_comparisons(tasks: list[Task]) -> list[tuple[Task, Task]]:
    """Returns a list of pairs of fluxnet tasks to run comparisons with.

    Pairs should be matching in science configurations and meteorological
    forcing, but differ in realisations. When multiple realisations are
    specified, return all pair wise combinations between all realisations.
    """
    return [
        (task_a, task_b)
        for task_a in tasks
        for task_b in tasks
        if task_a.met_forcing_file == task_b.met_forcing_file
        and task_a.sci_conf_id == task_b.sci_conf_id
        and task_a.branch_id < task_b.branch_id
        # TODO(Sean): Review later - the following code avoids using a double
        # for loop to generate pair wise combinations, however we would have
        # to re-initialize task instances to get access to the output file path
        # for each task. There is probably a better way but should be fine for
        # now...
        # for site in met_sites
        # for sci_conf_id in range(len(science_configurations))
        # for branch_id_first, branch_id_second in itertools.combinations(
        #     range(len(realisations)), 2
        # )
    ]
