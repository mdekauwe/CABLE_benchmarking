"""`pytest` tests for utils/subprocess.py"""

import subprocess
import pytest

from benchcab.utils.subprocess import run_cmd
from .common import TMP_DIR


def test_run_cmd(capfd):
    """Tests for `run_cmd()`."""

    # Success case: test stdout is suppressed in non-verbose mode
    run_cmd("echo foo")
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    # Success case: test stderr is suppressed in non-verbose mode
    run_cmd("echo foo 1>&2")
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    # Success case: test stdout is printed in verbose mode
    run_cmd("echo foo", verbose=True)
    captured = capfd.readouterr()
    assert captured.out == "echo foo\nfoo\n"
    assert captured.err == ""

    # Success case: test stderr is redirected to stdout in verbose mode
    run_cmd("echo foo 1>&2", verbose=True)
    captured = capfd.readouterr()
    assert captured.out == "echo foo 1>&2\nfoo\n"
    assert captured.err == ""

    # Success case: test output is captured with capture_output enabled
    proc = run_cmd("echo foo", capture_output=True)
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert proc.stdout == "foo\n"
    assert proc.stderr == ""

    # Success case: test command is printed in verbose mode
    proc = run_cmd("echo foo", capture_output=True, verbose=True)
    captured = capfd.readouterr()
    assert captured.out == "echo foo\n"
    assert captured.err == ""
    assert proc.stdout == "foo\n"
    assert proc.stderr == ""

    # Success case: redirect output to file descriptor
    file_path = TMP_DIR / "out.txt"
    run_cmd("echo foo", output_file=file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        assert file.read() == "foo\n"
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    # Success case: redirect output to file descriptor in verbose mode
    file_path = TMP_DIR / "out.txt"
    run_cmd("echo foo", output_file=file_path, verbose=True)
    with open(file_path, "r", encoding="utf-8") as file:
        assert file.read() == "foo\n"
    captured = capfd.readouterr()
    assert captured.out == "echo foo\n"
    assert captured.err == ""

    # Failure case: check non-zero return code throws an exception
    with pytest.raises(subprocess.CalledProcessError):
        run_cmd("exit 1")
