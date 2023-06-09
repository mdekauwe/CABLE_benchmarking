"""A module containing functions and data structures for running fluxnet tasks."""


import os
import shutil
import subprocess
import multiprocessing
import queue
import dataclasses
from pathlib import Path
from typing import TypeVar, Dict, Any

import flatdict
import netCDF4
import f90nml

from benchcab import internal
import benchcab.get_cable


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


def patch_namelist(nml_path: Path, patch: dict):
    """Writes a namelist patch specified by `patch` to `nml_path`.

    The `patch` dictionary must comply with the `f90nml` api.
    """

    if not nml_path.exists():
        f90nml.write(patch, nml_path)
        return

    nml = f90nml.read(nml_path)
    # remove namelist file as f90nml cannot write to an existing file
    nml_path.unlink()
    f90nml.write(deep_update(nml, patch), nml_path)


f90_logical_repr = {True: ".true.", False: ".false."}


class CableError(Exception):
    """Custom exception class for CABLE errors."""


@dataclasses.dataclass
class Task:
    """A class used to represent a single fluxnet task."""

    branch_id: int
    branch_name: str
    branch_patch: dict
    met_forcing_file: str
    sci_conf_id: int
    sci_config: dict

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

    def setup_task(self, verbose=False):
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

        self.clean_task(verbose=verbose)
        self.fetch_files(verbose=verbose)

        nml_path = (
            internal.CWD
            / internal.SITE_TASKS_DIR
            / self.get_task_name()
            / internal.CABLE_NML
        )

        if verbose:
            print(f"  Adding base configurations to CABLE namelist file {nml_path}")
        patch_namelist(
            nml_path,
            {
                "cable": {
                    "filename": {
                        "met": str(internal.MET_DIR / self.met_forcing_file),
                        "out": str(
                            internal.CWD
                            / internal.SITE_OUTPUT_DIR
                            / self.get_output_filename()
                        ),
                        "log": str(
                            internal.CWD
                            / internal.SITE_LOG_DIR
                            / self.get_log_filename()
                        ),
                        "restart_out": " ",
                        "type": str(internal.CWD / internal.GRID_FILE),
                    },
                    "output": {
                        "restart": False,
                    },
                    "fixedCO2": internal.CABLE_FIXED_CO2_CONC,
                    "casafile": {
                        "phen": str(internal.CWD / internal.PHEN_FILE),
                        "cnpbiome": str(internal.CWD / internal.CNPBIOME_FILE),
                    },
                    "spinup": False,
                }
            },
        )

        if verbose:
            print(f"  Adding science configurations to CABLE namelist file {nml_path}")
        patch_namelist(nml_path, self.sci_config)

        if self.branch_patch:
            if verbose:
                print(
                    f"  Adding branch specific configurations to CABLE namelist file {nml_path}"
                )
            patch_namelist(nml_path, self.branch_patch)

    def clean_task(self, verbose=False):
        """Cleans output files, namelist files, log files and cable executables if they exist."""

        if verbose:
            print("  Cleaning task")

        task_name = self.get_task_name()
        task_dir = Path(internal.CWD, internal.SITE_TASKS_DIR, task_name)

        if Path.exists(task_dir / internal.CABLE_EXE):
            os.remove(task_dir / internal.CABLE_EXE)

        if Path.exists(task_dir / internal.CABLE_NML):
            os.remove(task_dir / internal.CABLE_NML)

        if Path.exists(task_dir / internal.CABLE_VEGETATION_NML):
            os.remove(task_dir / internal.CABLE_VEGETATION_NML)

        if Path.exists(task_dir / internal.CABLE_SOIL_NML):
            os.remove(task_dir / internal.CABLE_SOIL_NML)

        output_file = self.get_output_filename()
        if Path.exists(internal.CWD / internal.SITE_OUTPUT_DIR / output_file):
            os.remove(internal.CWD / internal.SITE_OUTPUT_DIR / output_file)

        log_file = self.get_log_filename()
        if Path.exists(internal.CWD / internal.SITE_LOG_DIR / log_file):
            os.remove(internal.CWD / internal.SITE_LOG_DIR / log_file)

        return self

    def fetch_files(self, verbose=False):
        """Retrieves all files necessary to run cable in the task directory.

        Namely:
        - copies contents of 'namelists' directory to 'runs/site/tasks/<task_name>' directory.
        - copies cable executable from source to 'runs/site/tasks/<task_name>' directory.
        """

        task_dir = Path(internal.CWD, internal.SITE_TASKS_DIR, self.get_task_name())

        if verbose:
            print(
                f"  Copying namelist files from {internal.CWD / internal.NAMELIST_DIR} "
                f"to {task_dir}"
            )

        shutil.copytree(
            internal.CWD / internal.NAMELIST_DIR, task_dir, dirs_exist_ok=True
        )

        exe_src = (
            internal.CWD
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

    def run(self, verbose=False):
        """Runs a single fluxnet task."""
        task_name = self.get_task_name()
        task_dir = internal.CWD / internal.SITE_TASKS_DIR / task_name
        if verbose:
            print(
                f"Running task {task_name}... CABLE standard output "
                f"saved in {task_dir / internal.CABLE_STDOUT_FILENAME}"
            )
        try:
            self.run_cable(verbose=verbose)
            self.add_provenance_info(verbose=verbose)
        except CableError:
            return

    def run_cable(self, verbose=False):
        """Run the CABLE executable for the given task.

        Raises `CableError` when CABLE returns a non-zero exit code.
        """
        task_name = self.get_task_name()
        task_dir = internal.CWD / internal.SITE_TASKS_DIR / task_name
        exe_path = task_dir / internal.CABLE_EXE
        nml_path = task_dir / internal.CABLE_NML
        stdout_path = task_dir / internal.CABLE_STDOUT_FILENAME
        cmd = f"{exe_path} {nml_path} > {stdout_path} 2>&1"
        try:
            if verbose:
                print(f"  {cmd}")
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"Error: CABLE returned an error for task {task_name}")
            raise CableError from exc

    def add_provenance_info(self, verbose=False):
        """Adds provenance information to global attributes of netcdf output file.

        Attributes include branch url, branch revision number and key value pairs in
        the namelist file used to run cable.
        """
        nc_output_path = (
            internal.CWD / internal.SITE_OUTPUT_DIR / self.get_output_filename()
        )
        nml = f90nml.read(
            internal.CWD
            / internal.SITE_TASKS_DIR
            / self.get_task_name()
            / internal.CABLE_NML
        )
        if verbose:
            print(f"  Adding attributes to output file: {nc_output_path}")
        with netCDF4.Dataset(nc_output_path, "r+") as nc_output:
            nc_output.setncatts(
                {
                    **{
                        key: f90_logical_repr[val] if isinstance(val, bool) else val
                        for key, val in flatdict.FlatDict(
                            nml["cable"], delimiter="%"
                        ).items()
                    },
                    **{
                        "cable_branch": benchcab.get_cable.svn_info_show_item(
                            internal.CWD / internal.SRC_DIR / self.branch_name, "url"
                        ),
                        "svn_revision_number": benchcab.get_cable.svn_info_show_item(
                            internal.CWD / internal.SRC_DIR / self.branch_name,
                            "revision",
                        ),
                    },
                }
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


def run_tasks(tasks: list[Task], verbose=False):
    """Runs tasks in `tasks` serially."""
    for task in tasks:
        task.run(verbose=verbose)


def run_tasks_in_parallel(tasks: list[Task], verbose=False):
    """Runs tasks in `tasks` in parallel across multiple processes."""

    task_queue: multiprocessing.Queue = multiprocessing.Queue()
    for task in tasks:
        task_queue.put(task)

    processes = []
    for _ in range(internal.NCPUS):
        proc = multiprocessing.Process(target=worker_run, args=[task_queue, verbose])
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()


def worker_run(task_queue: multiprocessing.Queue, verbose=False):
    """Runs tasks in `task_queue` until the queue is emptied."""
    while True:
        try:
            task = task_queue.get_nowait()
        except queue.Empty:
            return
        task.run(verbose=verbose)


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


def get_comparison_name(task_a: Task, task_b: Task) -> str:
    """Returns the naming convention used for bitwise comparisons.

    Assumes `met_forcing_file` and `sci_conf_id` attributes are
    common to both tasks.
    """
    met_forcing_base_filename = task_a.met_forcing_file.split(".")[0]
    return (
        f"{met_forcing_base_filename}_S{task_a.sci_conf_id}"
        f"_R{task_a.branch_id}_R{task_b.branch_id}"
    )


def run_comparisons(comparisons: list[tuple[Task, Task]], verbose=False):
    """Runs bitwise comparison tasks serially."""
    for task_a, task_b in comparisons:
        run_comparison(task_a, task_b, verbose=verbose)


def run_comparisons_in_parallel(comparisons: list[tuple[Task, Task]], verbose=False):
    """Runs bitwise comparison tasks in parallel across multiple processes."""

    task_queue: multiprocessing.Queue = multiprocessing.Queue()
    for pair in comparisons:
        task_queue.put(pair)

    processes = []
    for _ in range(internal.NCPUS):
        proc = multiprocessing.Process(
            target=worker_comparison, args=[task_queue, verbose]
        )
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()


def worker_comparison(task_queue: multiprocessing.Queue, verbose=False):
    """Runs bitwise comparison tasks in `task_queue` until the queue is emptied."""
    while True:
        try:
            task_a, task_b = task_queue.get_nowait()
        except queue.Empty:
            return
        run_comparison(task_a, task_b, verbose=verbose)


def run_comparison(task_a: Task, task_b: Task, verbose=False):
    """Executes `nccmp -df` between the NetCDF output file of `task_a` and of `task_b`."""
    task_a_output = (
        internal.CWD / internal.SITE_OUTPUT_DIR / task_a.get_output_filename()
    )
    task_b_output = (
        internal.CWD / internal.SITE_OUTPUT_DIR / task_b.get_output_filename()
    )
    output_file = (
        internal.CWD
        / internal.SITE_BITWISE_CMP_DIR
        / f"{get_comparison_name(task_a, task_b)}.txt"
    )
    if verbose:
        print(
            f"Comparing files {task_a_output.name} and {task_b_output.name} bitwise..."
        )
    cmd = f"nccmp -df {task_a_output} {task_b_output} 2>&1"
    if verbose:
        print(f"  {cmd}")
    proc = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(proc.stdout)
        print(
            f"Failure: files {task_a_output.name} {task_b_output.name} differ. "
            f"Results of diff have been written to {output_file}"
        )
    else:
        print(f"Success: files {task_a_output.name} {task_b_output.name} are identical")
