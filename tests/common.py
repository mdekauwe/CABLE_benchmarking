"""Helper functions for `pytest`."""

import os
from pathlib import Path

TMP_DIR = Path(os.environ["TMPDIR"], "benchcab_tests")


def make_barebones_config() -> dict:
    """Returns a valid mock config."""
    conf = {
        "user": "foo1234",
        "project": "bar",
        "experiment": "five-site-test",
        "modules": [
            "intel-compiler/2021.1.1",
            "openmpi/4.1.0",
            "netcdf/4.7.4",
        ],
        "realisations": {
            0: {
                "name": "trunk",
                "revision": 9000,
                "trunk": True,
                "share_branch": False,
                "patch": {},
            },
            1: {
                "name": "v3.0-YP-changes",
                "revision": -1,
                "trunk": False,
                "share_branch": False,
                "patch": {
                    "cable": {"cable_user": {"ENABLE_SOME_FEATURE": False}}
                },
            },
        },
        "science_configurations": {
            "sci0": {
                "cable": {
                    "cable_user": {
                        "GS_SWITCH": "medlyn",
                        "FWSOIL_SWITCH": "Haverd2013",
                    }
                }
            },
            "sci1": {
                "cable": {
                    "cable_user": {
                        "GS_SWITCH": "leuning",
                        "FWSOIL_SWITCH": "Haverd2013",
                    }
                }
            },
        }
    }
    return conf
