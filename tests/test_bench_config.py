"""`pytest` tests for bench_config.py"""

import os
import pytest
import yaml

from tests.common import make_barebones_config, make_barbones_science_config
from benchcab.bench_config import check_config, read_config, check_science_config, read_science_config


def test_check_config():
    """Tests for `check_config()`."""

    # Success case: test barebones config is valid
    config = make_barebones_config()
    check_config(config)

    # Success case: test config is valid with arbitrary number of branch
    # keys defined
    config = make_barebones_config()
    config["foo_branch"] = {
        "name": "foo_branch",
        "revision": -1,
        "trunk": False,
        "share_branch": False,
    }
    config["bar_branch"] = {
        "name": "bar_branch",
        "revision": -1,
        "trunk": False,
        "share_branch": False,
    }
    check_config(config)

    # Success case: branch configuration with missing revision key
    config = make_barebones_config()
    config["user_branch"].pop("revision")
    check_config(config)

    # Failure case: test config without project key raises an exception
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config.pop("project")
        check_config(config)

    # Failure case: test config without user key raises an exception
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config.pop("user")
        check_config(config)

    # Failure case: test config without use_branches key raises an exception
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config.pop("use_branches")
        check_config(config)

    # Failure case: test config without modules key raises an exception
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config.pop("modules")
        check_config(config)

    # Failure case: test config without key of specified branch
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config.pop("trunk")
        check_config(config)

    # Failure case: test config when use_branches is greater than two
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config["use_branches"] += "my_new_branch"
        check_config(config)

    # Failure case: test config when use_branches is less than two
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config["use_branches"].pop()
        check_config(config)

    # Failure case: 'name' key is missing in branch configuration
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config["user_branch"].pop("name")
        check_config(config)

    # Failure case: 'trunk' key is missing in branch configuration
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config["user_branch"].pop("trunk")
        check_config(config)

    # Failure case: 'share_branch' key is missing in branch configuration
    with pytest.raises(ValueError):
        config = make_barebones_config()
        config["user_branch"].pop("share_branch")
        check_config(config)

    # Failure case: type of config["branch"]["revision"] is
    # not an integer
    with pytest.raises(TypeError):
        config = make_barebones_config()
        config["use_branches"] = ["foo_branch", "trunk"]
        config["foo_branch"] = {
            "name": "foo_branch",
            "revision": "-1",
            "trunk": False,
            "share_branch": False,
        }
        check_config(config)

    # Failure case: type of config["branch"]["trunk"] is
    # not an boolean
    with pytest.raises(TypeError):
        config = make_barebones_config()
        config["use_branches"] = ["foo_branch", "trunk"]
        config["foo_branch"] = {
            "name": "foo_branch",
            "revision": -1,
            "trunk": 0,
            "share_branch": False,
        }
        check_config(config)

    # Failure case: type of config["branch"]["share_branch"] is
    # not a boolean
    with pytest.raises(TypeError):
        config = make_barebones_config()
        config["use_branches"] = ["foo_branch", "trunk"]
        config["foo_branch"] = {
            "name": "foo_branch",
            "revision": -1,
            "trunk": False,
            "share_branch": "0"
        }
        check_config(config)


def test_read_config():
    """Tests for `read_config()`."""

    # Success case: write config to file, then read config from file
    config = make_barebones_config()
    filename = "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config == res

    # Success case: a specified branch with a missing revision number
    # should return a config with the default revision number
    config = make_barebones_config()
    config["trunk"].pop("revision")
    filename = "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert "revision" in res["trunk"] and res["trunk"]["revision"] == -1

    # Success case: config branch with missing key: met_subset
    # should return a config with met_subset = empty list
    config = make_barebones_config()
    config.pop("met_subset")
    filename = "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert "met_subset" in res and res["met_subset"] == []


def test_check_science_config():
    """Tests for `check_science_config()`."""

    # Success case: test barebones science config is valid
    science_config = make_barbones_science_config()
    check_science_config(science_config)

    # Failure case: outer dictionary key with invalid naming convention
    with pytest.raises(ValueError):
        science_config = make_barbones_science_config()
        science_config["science1"] = {"some_setting": True}
        check_science_config(science_config)

    # Failure case: outer dictionary key with invalid naming convention
    with pytest.raises(ValueError):
        science_config = make_barbones_science_config()
        science_config["sci_0"] = {"some_setting": True}
        check_science_config(science_config)

    # Failure case: outer dictionary key with invalid naming convention
    with pytest.raises(ValueError):
        science_config = make_barbones_science_config()
        science_config["sci"] = {"some_setting": True}
        check_science_config(science_config)

    # Failure case: outer dictionary key with invalid naming convention
    with pytest.raises(ValueError):
        science_config = make_barbones_science_config()
        science_config["0"] = {"some_setting": True}
        check_science_config(science_config)


def test_read_science_config():
    """Tests for `read_science_config()`."""

    # Success case: write science config to file, then read science config from file
    science_config = make_barbones_science_config()
    filename = "science-config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(science_config, file)

    res = read_science_config(filename)
    os.remove(filename)
    assert science_config == res
