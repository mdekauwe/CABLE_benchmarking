"""Helper functions for `pytest`."""


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
        "use_branches": ["user_branch", "trunk"],
        "user_branch": {
            "name": "v3.0-YP-changes",
            "revision": -1,
            "trunk": False,
            "share_branch": False,
        },
        "trunk": {
            "name": "trunk",
            "revision": 9000,
            "trunk": True,
            "share_branch": False,
        },
    }
    return conf


def make_barbones_science_config() -> dict:
    """Returns a valid mock science config."""
    sci_conf = {
        "sci01": "",
        "sci02": "",
    }
    return sci_conf
