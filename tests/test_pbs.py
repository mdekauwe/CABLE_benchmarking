"""`pytest` tests for utils/pbs.py"""

from benchcab.utils.pbs import render_job_script
from benchcab import internal


def test_render_job_script():
    """Tests for `render_job_script()`."""

    # Success case: test default job script generated is correct
    assert render_job_script(
        project="tm70",
        config_path="/path/to/config.yaml",
        modules=["foo", "bar", "baz"],
        storage_flags=["scratch/tm70"],
        benchcab_path="/absolute/path/to/benchcab",
    ) == (
        f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+scratch/tm70

module purge
module load foo
module load bar
module load baz

/absolute/path/to/benchcab fluxsite-run-tasks --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-run-tasks failed. Exiting...'
    exit 1
fi

/absolute/path/to/benchcab fluxsite-bitwise-cmp --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-bitwise-cmp failed. Exiting...'
    exit 1
fi
"""
    )

    # Success case: test verbose flag is added to command line arguments
    assert render_job_script(
        project="tm70",
        config_path="/path/to/config.yaml",
        modules=["foo", "bar", "baz"],
        storage_flags=["scratch/tm70"],
        verbose=True,
        benchcab_path="/absolute/path/to/benchcab",
    ) == (
        f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+scratch/tm70

module purge
module load foo
module load bar
module load baz

/absolute/path/to/benchcab fluxsite-run-tasks --config=/path/to/config.yaml -v
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-run-tasks failed. Exiting...'
    exit 1
fi

/absolute/path/to/benchcab fluxsite-bitwise-cmp --config=/path/to/config.yaml -v
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-bitwise-cmp failed. Exiting...'
    exit 1
fi
"""
    )

    # Success case: skip fluxsite-bitwise-cmp step
    assert render_job_script(
        project="tm70",
        config_path="/path/to/config.yaml",
        modules=["foo", "bar", "baz"],
        storage_flags=["scratch/tm70"],
        skip_bitwise_cmp=True,
        benchcab_path="/absolute/path/to/benchcab",
    ) == (
        f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+scratch/tm70

module purge
module load foo
module load bar
module load baz

/absolute/path/to/benchcab fluxsite-run-tasks --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-run-tasks failed. Exiting...'
    exit 1
fi

"""
    )

    # Success case: test with storage_flags set to []
    assert render_job_script(
        project="tm70",
        config_path="/path/to/config.yaml",
        modules=["foo", "bar", "baz"],
        storage_flags=[],
        skip_bitwise_cmp=True,
        benchcab_path="/absolute/path/to/benchcab",
    ) == (
        f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70

module purge
module load foo
module load bar
module load baz

/absolute/path/to/benchcab fluxsite-run-tasks --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxsite-run-tasks failed. Exiting...'
    exit 1
fi

"""
    )
