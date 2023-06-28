"""Contains functions for job script creation and submission on Gadi."""

from subprocess import CalledProcessError
from pathlib import Path

from benchcab import internal
from benchcab.utils import subprocess


def get_local_storage_flag(path: Path) -> str:
    """Returns the PBS storage flag for a path on the Gadi file system."""
    if str(path).startswith("/scratch"):
        return f"scratch/{path.parts[2]}"
    if str(path).startswith("/g/data"):
        return f"gdata/{path.parts[3]}"
    raise RuntimeError("Current directory structure unknown on Gadi.")


def submit_job(
    project: str,
    config_path: str,
    modules: list,
    verbose=False,
    skip_bitwise_cmp=False,
):
    """Submits a PBS job that executes all computationally expensive commands.

    This includes things such as running CABLE and running bitwise comparison jobs
    between model output files.
    The PBS job script is written to the current working directory as a side effect.
    """

    job_script_path = internal.CWD / internal.QSUB_FNAME
    module_load_lines = "\n".join(
        f"module load {module_name}" for module_name in modules
    )
    verbose_flag = "-v" if verbose else ""

    print(
        "Creating PBS job script to run FLUXNET tasks on compute "
        f"nodes: {job_script_path.relative_to(internal.CWD)}"
    )
    with open(job_script_path, "w", encoding="utf-8") as file:
        file.write(
            f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P {project}
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/{project}+{get_local_storage_flag(internal.CWD)}

module purge
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
{module_load_lines}

benchcab fluxnet-run-tasks --config={config_path} {verbose_flag}
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-run-tasks failed. Exiting...'
    exit 1
fi
{'' if skip_bitwise_cmp else f'''
benchcab fluxnet-bitwise-cmp --config={config_path} {verbose_flag}
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-bitwise-cmp failed. Exiting...'
    exit 1
fi''' }
"""
        )

    try:
        proc = subprocess.run_cmd(
            f"qsub {job_script_path}", capture_output=True, verbose=verbose
        )
        print(f"PBS job submitted: {proc.stdout.strip()}")
    except CalledProcessError as exc:
        print("Error when submitting job to NCI queue")
        print(exc.stderr)
        raise
