"""Helper functions for `pytest`."""

from pathlib import Path

TMP_DIR = Path.cwd() / "tests" / "tmp"


def make_barebones_config() -> dict:
    """Returns a valid mock config."""
    conf = {
        "user": "foo1234",
        "project": "bar",
        "met_subset": [],
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
            },
            1: {
                "name": "v3.0-YP-changes",
                "revision": -1,
                "trunk": False,
                "share_branch": False,
            },
        },
    }
    return conf


def make_barbones_science_config() -> dict:
    """Returns a valid mock science config."""
    sci_conf = {
        "sci0": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        },
        "sci1": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "Haverd2013"
            }
        },
    }

    return sci_conf
