"""Helper functions for `pytest`."""

import tempfile
from pathlib import Path

TMP_DIR = Path(tempfile.mkdtemp(prefix="benchcab_tests"))


def make_barebones_config() -> dict:
    """Returns a valid mock config."""
    conf = {
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
    }
    return conf
