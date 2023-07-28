"""Helper functions for `pytest`."""

import tempfile
from subprocess import CompletedProcess, CalledProcessError
from pathlib import Path
from typing import Optional

from benchcab.utils.subprocess import SubprocessWrapperInterface
from benchcab.environment_modules import EnvironmentModulesInterface

MOCK_CWD = TMP_DIR = Path(tempfile.mkdtemp(prefix="benchcab_tests"))


def get_mock_config() -> dict:
    """Returns a valid mock config."""
    config = {
        "project": "bar",
        "experiment": "five-site-test",
        "modules": [
            "intel-compiler/2021.1.1",
            "openmpi/4.1.0",
            "netcdf/4.7.4",
        ],
        "realisations": [
            {
                "name": "trunk",
                "revision": 9000,
                "path": "trunk",
                "patch": {},
                "build_script": "",
            },
            {
                "name": "v3.0-YP-changes",
                "revision": -1,
                "path": "branches/Users/sean/my-branch",
                "patch": {"cable": {"cable_user": {"ENABLE_SOME_FEATURE": False}}},
                "build_script": "",
            },
        ],
        "science_configurations": [
            {
                "cable": {
                    "cable_user": {
                        "GS_SWITCH": "medlyn",
                        "FWSOIL_SWITCH": "Haverd2013",
                    }
                }
            },
            {
                "cable": {
                    "cable_user": {
                        "GS_SWITCH": "leuning",
                        "FWSOIL_SWITCH": "Haverd2013",
                    }
                }
            },
        ],
        "pbs": {
            "ncpus": 16,
            "mem": "64G",
            "walltime": "01:00:00",
            "storage": ["gdata/foo123"],
        },
        "multiprocessing": True,
    }
    return config


class MockSubprocessWrapper(SubprocessWrapperInterface):
    """A mock implementation of `SubprocessWrapperInterface` used for testing."""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.stdout = "mock standard output"
        self.error_on_call = False

    def run_cmd(
        self,
        cmd: str,
        capture_output: bool = False,
        output_file: Optional[Path] = None,
        verbose: bool = False,
    ) -> CompletedProcess:
        self.commands.append(cmd)
        if self.error_on_call:
            raise CalledProcessError(returncode=1, cmd=cmd, output=self.stdout)
        if output_file:
            output_file.touch()
        return CompletedProcess(cmd, returncode=0, stdout=self.stdout)


class MockEnvironmentModules(EnvironmentModulesInterface):
    """A mock implementation of `EnvironmentModulesInterface` used for testing."""

    def __init__(self) -> None:
        self.commands: list[str] = []

    def module_is_avail(self, *args: str) -> bool:
        self.commands.append("module is-avail " + " ".join(args))
        return True

    def module_is_loaded(self, *args: str) -> bool:
        self.commands.append("module is-loaded " + " ".join(args))
        return True

    def module_load(self, *args: str) -> None:
        self.commands.append("module load " + " ".join(args))

    def module_unload(self, *args: str) -> None:
        self.commands.append("module unload " + " ".join(args))
