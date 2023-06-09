"""`pytest` tests for bench_config.py"""

import os
import pytest
import yaml

from tests.common import TMP_DIR
from tests.common import make_barebones_config
from benchcab.bench_config import check_config, read_config
from benchcab import internal


def test_check_config():
    """Tests for `check_config()`."""

    # Success case: test barebones config is valid
    config = make_barebones_config()
    check_config(config)

    # Success case: branch configuration with missing name key
    config = make_barebones_config()
    config["realisations"][0].pop("name")
    check_config(config)

    # Success case: branch configuration with missing revision key
    config = make_barebones_config()
    config["realisations"][0].pop("revision")
    check_config(config)

    # Success case: branch configuration with missing patch key
    config = make_barebones_config()
    config["realisations"][0].pop("patch")
    check_config(config)

    # Success case: test config when realisations contains more than two keys
    config = make_barebones_config()
    config["realisations"].append({"path": "path/to/my_new_branch"})
    assert len(config["realisations"]) > 2
    check_config(config)

    # Success case: test config when realisations contains less than two keys
    config = make_barebones_config()
    config["realisations"].pop()
    assert len(config["realisations"]) < 2
    check_config(config)

    # Success case: test experiment with site id from the
    # five-site-test is valid
    config = make_barebones_config()
    config["experiment"] = "AU-Tum"
    check_config(config)

    # Success case: test config without science_configurations is valid
    config = make_barebones_config()
    config.pop("science_configurations")
    check_config(config)

    # Failure case: test config without project key raises an exception
    with pytest.raises(
        ValueError,
        match="The config file does not list all required entries. "
        "Those are: " + ", ".join(internal.CONFIG_REQUIRED_KEYS),
    ):
        config = make_barebones_config()
        config.pop("project")
        check_config(config)

    # Failure case: test config without realisations key raises an exception
    with pytest.raises(
        ValueError,
        match="The config file does not list all required entries. "
        "Those are: " + ", ".join(internal.CONFIG_REQUIRED_KEYS),
    ):
        config = make_barebones_config()
        config.pop("realisations")
        check_config(config)

    # Failure case: test config with empty realisations key raises an exception
    with pytest.raises(ValueError, match="The 'realisations' key cannot be empty."):
        config = make_barebones_config()
        config["realisations"] = []
        check_config(config)

    # Failure case: test config without modules key raises an exception
    with pytest.raises(
        ValueError,
        match="The config file does not list all required entries. "
        "Those are: " + ", ".join(internal.CONFIG_REQUIRED_KEYS),
    ):
        config = make_barebones_config()
        config.pop("modules")
        check_config(config)

    # Failure case: test config without experiment key raises an exception
    with pytest.raises(
        ValueError,
        match="The config file does not list all required entries. "
        "Those are: " + ", ".join(internal.CONFIG_REQUIRED_KEYS),
    ):
        config = make_barebones_config()
        config.pop("experiment")
        check_config(config)

    # Failure case: test config with invalid experiment key raises an exception
    with pytest.raises(
        ValueError,
        match="The 'experiment' key is invalid.\n"
        "Valid experiments are: "
        + ", ".join(
            list(internal.MEORG_EXPERIMENTS)
            + internal.MEORG_EXPERIMENTS["five-site-test"]
        ),
    ):
        config = make_barebones_config()
        config["experiment"] = "foo"
        check_config(config)

    # Failure case: test config with invalid experiment key (not a subset of
    # five-site-test) raises an exception
    with pytest.raises(
        ValueError,
        match="The 'experiment' key is invalid.\n"
        "Valid experiments are: "
        + ", ".join(
            list(internal.MEORG_EXPERIMENTS)
            + internal.MEORG_EXPERIMENTS["five-site-test"]
        ),
    ):
        config = make_barebones_config()
        config["experiment"] = "CH-Dav"
        check_config(config)

    # Failure case: 'path' key is missing in branch configuration
    with pytest.raises(
        ValueError, match="Realisation '1' must specify the `path` field."
    ):
        config = make_barebones_config()
        config["realisations"][1].pop("path")
        check_config(config)

    # Failure case: test config with empty science_configurations key
    # raises an exception
    with pytest.raises(
        ValueError, match="The 'science_configurations' key cannot be empty."
    ):
        config = make_barebones_config()
        config["science_configurations"] = []
        check_config(config)

    # Failure case: project key is not a string
    with pytest.raises(TypeError, match="The 'project' key must be a string."):
        config = make_barebones_config()
        config["project"] = 123
        check_config(config)

    # Failure case: realisations key is not a list
    with pytest.raises(TypeError, match="The 'realisations' key must be a list."):
        config = make_barebones_config()
        config["realisations"] = {"foo": "bar"}
        check_config(config)

    # Failure case: realisations key is not a list of dict
    with pytest.raises(TypeError, match="Realisation '0' must be a dictionary object."):
        config = make_barebones_config()
        config["realisations"] = ["foo"]
        check_config(config)

    # Failure case: type of name is not a string
    with pytest.raises(
        TypeError, match="The 'name' field in realisation '1' must be a string."
    ):
        config = make_barebones_config()
        config["realisations"][1]["name"] = 1234
        check_config(config)

    # Failure case: type of path is not a string
    with pytest.raises(
        TypeError, match="The 'path' field in realisation '1' must be a string."
    ):
        config = make_barebones_config()
        config["realisations"][1]["path"] = 1234
        check_config(config)

    # Failure case: type of revision key is not an integer
    with pytest.raises(
        TypeError, match="The 'revision' field in realisation '1' must be an integer."
    ):
        config = make_barebones_config()
        config["realisations"][1]["revision"] = "-1"
        check_config(config)

    # Failure case: type of patch key is not a dictionary
    with pytest.raises(
        TypeError,
        match="The 'patch' field in realisation '1' must be a dictionary that is "
        "compatible with the f90nml python package.",
    ):
        config = make_barebones_config()
        config["realisations"][1]["patch"] = r"cable_user%ENABLE_SOME_FEATURE = .FALSE."
        check_config(config)

    # Failure case: type of build_script key is not a string
    with pytest.raises(
        TypeError, match="The 'build_script' field in realisation '1' must be a string."
    ):
        config = make_barebones_config()
        config["realisations"][1]["build_script"] = ["echo", "hello"]
        check_config(config)

    # Failure case: modules key is not a list
    with pytest.raises(TypeError, match="The 'modules' key must be a list."):
        config = make_barebones_config()
        config["modules"] = "netcdf"
        check_config(config)

    # Failure case: experiment key is not a string
    with pytest.raises(TypeError, match="The 'experiment' key must be a string."):
        config = make_barebones_config()
        config["experiment"] = 0
        check_config(config)

    # Failure case: type of config["science_configurations"] is not a list
    with pytest.raises(
        TypeError, match="The 'science_configurations' key must be a list."
    ):
        config = make_barebones_config()
        config["science_configurations"] = r"cable_user%GS_SWITCH = 'medlyn'"
        check_config(config)

    # Failure case: type of config["science_configurations"] is not a list of dict
    with pytest.raises(
        TypeError,
        match="Science config settings must be specified using a dictionary "
        "that is compatible with the f90nml python package.",
    ):
        config = make_barebones_config()
        config["science_configurations"] = [r"cable_user%GS_SWITCH = 'medlyn'"]
        check_config(config)


def test_read_config():
    """Tests for `read_config()`."""

    # Success case: write config to file, then read config from file
    config = make_barebones_config()
    filename = TMP_DIR / "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config == res

    # Success case: a specified branch with a missing name key
    # should return a config with name set to the base name of
    # the path key
    config = make_barebones_config()
    config["realisations"][0].pop("name")
    filename = TMP_DIR / "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert res["realisations"][0]["name"] == os.path.basename(
        config["realisations"][0]["path"]
    )

    # Success case: a specified branch with a missing revision number
    # should return a config with the default revision number
    config = make_barebones_config()
    config["realisations"][0].pop("revision")
    filename = TMP_DIR / "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert res["realisations"][0]["revision"] == -1

    # Success case: a specified branch with a missing patch dictionary
    # should return a config with patch set to its default value
    config = make_barebones_config()
    config["realisations"][0].pop("patch")
    filename = TMP_DIR / "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert res["realisations"][0]["patch"] == {}

    # Success case: a config with missing science_configurations key should return a
    # config with config['science_configurations'] set to its default value
    config = make_barebones_config()
    config.pop("science_configurations")
    filename = TMP_DIR / "config-barebones.yaml"

    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(config, file)

    res = read_config(filename)
    os.remove(filename)
    assert config != res
    assert res["science_configurations"] == internal.DEFAULT_SCIENCE_CONFIGURATIONS
