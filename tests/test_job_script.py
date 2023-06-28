"""`pytest` tests for job_script.py"""

import unittest.mock
import io
import subprocess
import contextlib
from pathlib import Path
import pytest

from benchcab import internal
from benchcab.job_script import get_local_storage_flag, submit_job
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


def test_submit_job():
    """Tests for `submit_job()`."""

    # Success case: test qsub command is executed
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag", autospec=True
    ) as mock_get_local_storage_flag, unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        mock_get_local_storage_flag.return_value = "storage_flag"
        submit_job(
            project="tm70",
            config_path="/path/to/config.yaml",
            modules=["foo", "bar", "baz"],
        )
        mock_run_cmd.assert_called_once_with(
            f"qsub {MOCK_CWD/internal.QSUB_FNAME}", capture_output=True, verbose=False
        )

    # Success case: test qsub command is executed with verbose enabled
    # TODO(Sean): this test should be removed once we use the logging module
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag", autospec=True
    ) as mock_get_local_storage_flag, unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        mock_get_local_storage_flag.return_value = "storage_flag"
        submit_job(
            project="tm70",
            config_path="/path/to/config.yaml",
            modules=["foo", "bar", "baz"],
            verbose=True,
        )
        mock_run_cmd.assert_called_once_with(
            f"qsub {MOCK_CWD/internal.QSUB_FNAME}", capture_output=True, verbose=True
        )

    # Success case: test default job script generated is correct
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag", autospec=True
    ) as mock_get_local_storage_flag, unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd",
    ):
        mock_get_local_storage_flag.return_value = "storage_flag"
        submit_job(
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
        "benchcab.job_script.get_local_storage_flag", autospec=True
    ) as mock_get_local_storage_flag, unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd"
    ):
        mock_get_local_storage_flag.return_value = "storage_flag"
        submit_job(
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

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ), unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd, unittest.mock.patch(
        "subprocess.CompletedProcess", autospec=True
    ) as mock_completed_process:
        mock_completed_process.configure_mock(stdout="standard output from qsub")
        mock_run_cmd.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            submit_job(
                project="tm70",
                config_path="/path/to/config.yaml",
                modules=["foo", "bar", "baz"],
            )
        assert buf.getvalue() == (
            "Creating PBS job script to run FLUXNET tasks on compute "
            f"nodes: {internal.QSUB_FNAME}\n"
            "PBS job submitted: standard output from qsub\n"
        )

    # Success case: add verbose flag to job script
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag", autospec=True
    ) as mock_get_local_storage_flag, unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd"
    ):
        mock_get_local_storage_flag.return_value = "storage_flag"
        submit_job(
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

    # Failure case: qsub non-zero exit code prints an error message
    with unittest.mock.patch(
        "benchcab.job_script.get_local_storage_flag"
    ), unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd:
        mock_run_cmd.side_effect = subprocess.CalledProcessError(
            1, "dummy-cmd", stderr="standard error from qsub"
        )
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            with pytest.raises(subprocess.CalledProcessError):
                submit_job(
                    project="tm70",
                    config_path="/path/to/config.yaml",
                    modules=["foo", "bar", "baz"],
                )
        assert buf.getvalue() == (
            "Creating PBS job script to run FLUXNET tasks on compute "
            f"nodes: {internal.QSUB_FNAME}\n"
            "Error when submitting job to NCI queue\nstandard error from qsub\n"
        )
