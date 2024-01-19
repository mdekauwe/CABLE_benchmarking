# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""Contains helper functions for manipulating PBS job scripts."""

from typing import Optional

from benchcab import internal


def render_job_script(
    project: str,
    config_path: str,
    modules: list,
    benchcab_path: str,
    verbose=False,
    skip_bitwise_cmp=False,
    pbs_config: Optional[dict] = None,
) -> str:
    """Returns the text for a PBS job script that executes all computationally expensive commands.

    This includes things such as running CABLE and running bitwise comparison jobs
    between model output files.
    """
    if pbs_config is None:
        pbs_config = internal.FLUXSITE_DEFAULT_PBS

    module_load_lines = "\n".join(
        f"module load {module_name}" for module_name in modules
    )
    verbose_flag = "-v" if verbose else ""
    storage_flags = [
        "gdata/ks32",
        "gdata/hh5",
        *pbs_config["storage"]
    ]
    return f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={pbs_config["ncpus"]}
#PBS -l mem={pbs_config["mem"]}
#PBS -l walltime={pbs_config["walltime"]}
#PBS -q normal
#PBS -P {project}
#PBS -j oe
#PBS -m e
#PBS -l storage={'+'.join(storage_flags)}

module purge
{module_load_lines}

set -ev

{benchcab_path} fluxsite-run-tasks --config={config_path} {verbose_flag}
{'' if skip_bitwise_cmp else f'''
{benchcab_path} fluxsite-bitwise-cmp --config={config_path} {verbose_flag}
''' }
"""
