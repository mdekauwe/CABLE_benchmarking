"""Contains helper functions for manipulating PBS job scripts."""

from benchcab import internal


def render_job_script(
    project: str,
    config_path: str,
    modules: list,
    storage_flags: list,
    verbose=False,
    skip_bitwise_cmp=False,
) -> str:
    """Returns a PBS job that executes all computationally expensive commands.

    This includes things such as running CABLE and running bitwise comparison jobs
    between model output files. The PBS job script is written to the current
    working directory as a side effect.
    """

    module_load_lines = "\n".join(
        f"module load {module_name}" for module_name in modules
    )
    verbose_flag = "-v" if verbose else ""
    storage_flags = ["gdata/ks32", "gdata/hh5", f"gdata/{project}", *storage_flags]
    return f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P {project}
#PBS -j oe
#PBS -m e
#PBS -l storage={'+'.join(storage_flags)}

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
