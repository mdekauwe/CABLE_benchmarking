"""A module containing utility functions that wraps around the `subprocess` module."""

import subprocess
import contextlib
import pathlib
from typing import Any, Optional


def run_cmd(
    cmd: str,
    capture_output: bool = False,
    output_file: Optional[pathlib.Path] = None,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """Helper function that wraps around `subprocess.run()`"""

    kwargs: Any = {}
    with contextlib.ExitStack() as stack:
        if capture_output:
            kwargs["capture_output"] = True
            kwargs["text"] = True
        else:
            if output_file:
                kwargs["stdout"] = stack.enter_context(
                    output_file.open("w", encoding="utf-8")
                )
            else:
                kwargs["stdout"] = None if verbose else subprocess.DEVNULL
            kwargs["stderr"] = subprocess.STDOUT

        if verbose:
            print(cmd)
        proc = subprocess.run(cmd, shell=True, check=True, **kwargs)

    return proc
