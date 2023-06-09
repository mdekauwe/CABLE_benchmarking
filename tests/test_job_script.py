"""`pytest` tests for job_script.py"""

import unittest.mock
import io
import subprocess
import contextlib
from pathlib import Path
import pytest

from benchcab import internal
from benchcab.job_script import get_local_storage_flag, create_job_script, submit_job
from .common import MOCK_CWD


def test_get_local_storage_flag():
    """Tests for `get_local_storage_flag()`."""

    # Success case: scratch dir storage flag
    assert get_local_storage_flag(Path("/scratch/tm70/foo")) == "scratch/tm70"

    # Success case: gdata storage flag
    assert get_local_storage_flag(Path("/g/data/tm70/foo")) == "gdata/tm70"

    # Failure case: invalid path
    with pytest.raises(
        RuntimeError, match="Current directory structure unknown on Gadi."
    ):
        get_local_storage_flag(Path("/home/189/foo"))


def test_create_job_script():
    """Tests for `create_job_script()`."""

    # Success case: test default job script creation
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ) as mock_get_local_storage_flag:
        mock_get_local_storage_flag.return_value = "storage_flag"
        create_job_script(
            project="tm70",
            config_path="/path/to/config.yaml",
            modules=["foo", "bar", "baz"],
        )
    with open(MOCK_CWD / internal.QSUB_FNAME, "r", encoding="utf-8") as file:
        assert (
            file.read()
            == f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+storage_flag

module purge
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
module load foo
module load bar
module load baz

benchcab fluxnet-run-tasks --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-run-tasks failed. Exiting...'
    exit 1
fi

benchcab fluxnet-bitwise-cmp --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-bitwise-cmp failed. Exiting...'
    exit 1
fi
"""
        )

    # Success case: skip fluxnet-bitwise-cmp step
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ) as mock_get_local_storage_flag:
        mock_get_local_storage_flag.return_value = "storage_flag"
        create_job_script(
            project="tm70",
            config_path="/path/to/config.yaml",
            modules=["foo", "bar", "baz"],
            skip_bitwise_cmp=True,
        )
    with open(MOCK_CWD / internal.QSUB_FNAME, "r", encoding="utf-8") as file:
        assert (
            file.read()
            == f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+storage_flag

module purge
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
module load foo
module load bar
module load baz

benchcab fluxnet-run-tasks --config=/path/to/config.yaml 
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-run-tasks failed. Exiting...'
    exit 1
fi

"""
        )

    # Success case: test standard output
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ) as mock_get_local_storage_flag:
        mock_get_local_storage_flag.return_value = "storage_flag"
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            create_job_script(
                project="tm70",
                config_path="/path/to/config.yaml",
                modules=["foo", "bar", "baz"],
            )
        assert buf.getvalue() == (
            "Creating PBS job script to run FLUXNET tasks on compute "
            f"nodes: {internal.QSUB_FNAME}\n"
        )

    # Success case: enable verbose flag
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ) as mock_get_local_storage_flag:
        mock_get_local_storage_flag.return_value = "storage_flag"
        create_job_script(
            project="tm70",
            config_path="/path/to/config.yaml",
            modules=["foo", "bar", "baz"],
            verbose=True,
        )
    with open(MOCK_CWD / internal.QSUB_FNAME, "r", encoding="utf-8") as file:
        assert (
            file.read()
            == f"""#!/bin/bash
#PBS -l wd
#PBS -l ncpus={internal.NCPUS}
#PBS -l mem={internal.MEM}
#PBS -l walltime={internal.WALL_TIME}
#PBS -q normal
#PBS -P tm70
#PBS -j oe
#PBS -m e
#PBS -l storage=gdata/ks32+gdata/hh5+gdata/tm70+storage_flag

module purge
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
module load foo
module load bar
module load baz

benchcab fluxnet-run-tasks --config=/path/to/config.yaml -v
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-run-tasks failed. Exiting...'
    exit 1
fi

benchcab fluxnet-bitwise-cmp --config=/path/to/config.yaml -v
if [ $? -ne 0 ]; then
    echo 'Error: benchcab fluxnet-bitwise-cmp failed. Exiting...'
    exit 1
fi
"""
        )


def test_submit_job():
    """Tests for `submit_job()`."""

    # Success case: submit PBS job
    with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
        submit_job()
        mock_subprocess_run.assert_called_once_with(
            f"qsub {MOCK_CWD/internal.QSUB_FNAME}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

    # Success case: test standard output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(stdout="standard output from qsub")
        mock_subprocess_run.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            submit_job()
        assert buf.getvalue() == "PBS job submitted: standard output from qsub\n"

    # Failure case: qsub non-zero exit code
    with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "dummy-cmd", stderr="standard error from qsub"
        )
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            with pytest.raises(subprocess.CalledProcessError):
                submit_job()
        assert buf.getvalue() == (
            "Error when submitting job to NCI queue\n" "standard error from qsub\n"
        )
