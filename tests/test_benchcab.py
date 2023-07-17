"""`pytest` tests for benchcab.py"""

import contextlib
import io
from subprocess import CalledProcessError
import pytest

from benchcab.benchcab import Benchcab
from benchcab import internal
from benchcab.utils.subprocess import SubprocessWrapperInterface
from .common import MockSubprocessWrapper, get_mock_config, MOCK_CWD


def get_mock_app(
    subprocess_handler: SubprocessWrapperInterface = MockSubprocessWrapper(),
) -> Benchcab:
    """Returns a mock `Benchcab` instance for testing against."""
    config = get_mock_config()
    app = Benchcab(argv=["benchcab", "fluxsite"], config=config, validate_env=False)
    app.subprocess_handler = subprocess_handler
    app.root_dir = MOCK_CWD
    return app


def test_fluxsite_submit_job():
    """Tests for `Benchcab.fluxsite_submit_job()`."""

    # Success case: test qsub command is executed
    mock_subprocess = MockSubprocessWrapper()
    app = get_mock_app(mock_subprocess)
    app.fluxsite_submit_job()
    assert f"qsub {MOCK_CWD / internal.QSUB_FNAME}" in mock_subprocess.commands

    # Success case: test non-verbose output
    app = get_mock_app()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        app.fluxsite_submit_job()
    assert buf.getvalue() == (
        "Creating PBS job script to run fluxsite tasks on compute "
        f"nodes: {internal.QSUB_FNAME}\n"
        f"PBS job submitted: {mock_subprocess.stdout}\n"
        "The CABLE log file for each task is written to "
        f"{internal.FLUXSITE_LOG_DIR}/<task_name>_log.txt\n"
        "The CABLE standard output for each task is written to "
        f"{internal.FLUXSITE_TASKS_DIR}/<task_name>/out.txt\n"
        "The NetCDF output for each task is written to "
        f"{internal.FLUXSITE_OUTPUT_DIR}/<task_name>_out.nc\n"
    )

    # Failure case: qsub non-zero exit code prints an error message
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.error_on_call = True
    app = get_mock_app(subprocess_handler=mock_subprocess)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        with pytest.raises(CalledProcessError):
            app.fluxsite_submit_job()
    assert buf.getvalue() == (
        "Creating PBS job script to run fluxsite tasks on compute "
        f"nodes: {internal.QSUB_FNAME}\n"
        f"Error when submitting job to NCI queue\n{mock_subprocess.stdout}\n"
    )
