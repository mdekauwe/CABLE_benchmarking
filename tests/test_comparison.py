"""`pytest` tests for `comparison.py`."""

import contextlib
import io

from benchcab import internal
from benchcab.comparison import ComparisonTask
from benchcab.utils.subprocess import SubprocessWrapperInterface

from .common import MOCK_CWD, MockSubprocessWrapper


def get_mock_comparison_task(
    subprocess_handler: SubprocessWrapperInterface = MockSubprocessWrapper(),
) -> ComparisonTask:
    """Returns a mock `ComparisonTask` instance for testing against."""
    comparison_task = ComparisonTask(
        files=(MOCK_CWD / "file_a.nc", MOCK_CWD / "file_b.nc"),
        task_name="mock_comparison_task_name",
    )
    comparison_task.subprocess_handler = subprocess_handler
    comparison_task.root_dir = MOCK_CWD
    return comparison_task


def test_run_comparison():
    """Tests for `run_comparison()`."""
    file_a = MOCK_CWD / "file_a.nc"
    file_b = MOCK_CWD / "file_b.nc"
    bitwise_cmp_dir = MOCK_CWD / internal.FLUXSITE_BITWISE_CMP_DIR
    bitwise_cmp_dir.mkdir(parents=True)

    # Success case: run comparison
    mock_subprocess = MockSubprocessWrapper()
    task = get_mock_comparison_task(subprocess_handler=mock_subprocess)
    task.run()
    assert f"nccmp -df {file_a} {file_b}" in mock_subprocess.commands

    # Success case: test non-verbose output
    task = get_mock_comparison_task()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run()
    assert (
        buf.getvalue() == f"Success: files {file_a.name} {file_b.name} are identical\n"
    )

    # Success case: test verbose output
    task = get_mock_comparison_task()
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run(verbose=True)
    assert buf.getvalue() == (
        f"Comparing files {file_a.name} and {file_b.name} bitwise...\n"
        f"Success: files {file_a.name} {file_b.name} are identical\n"
    )

    # Failure case: test failed comparison check (files differ)
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.error_on_call = True
    task = get_mock_comparison_task(subprocess_handler=mock_subprocess)
    stdout_file = bitwise_cmp_dir / f"{task.task_name}.txt"
    task.run()
    with stdout_file.open("r", encoding="utf-8") as file:
        assert file.read() == mock_subprocess.stdout

    # Failure case: test non-verbose standard output on failure
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.error_on_call = True
    task = get_mock_comparison_task(subprocess_handler=mock_subprocess)
    stdout_file = bitwise_cmp_dir / f"{task.task_name}.txt"
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run()
    assert buf.getvalue() == (
        f"Failure: files {file_a.name} {file_b.name} differ. Results of diff "
        f"have been written to {stdout_file}\n"
    )

    # Failure case: test verbose standard output on failure
    mock_subprocess = MockSubprocessWrapper()
    mock_subprocess.error_on_call = True
    task = get_mock_comparison_task(subprocess_handler=mock_subprocess)
    stdout_file = bitwise_cmp_dir / f"{task.task_name}.txt"
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run(verbose=True)
    assert buf.getvalue() == (
        f"Comparing files {file_a.name} and {file_b.name} bitwise...\n"
        f"Failure: files {file_a.name} {file_b.name} differ. Results of diff "
        f"have been written to {stdout_file}\n"
    )
