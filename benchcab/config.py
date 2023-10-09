"""A module containing all *_config() functions."""

from pathlib import Path

import yaml

from benchcab import internal


def check_config(config: dict):
    """Performs input validation on config file.

    If the config is invalid, an exception is raised. Otherwise, do nothing.
    """
    if any(key not in config for key in internal.CONFIG_REQUIRED_KEYS):
        raise ValueError(
            "Keys are missing from the config file: "
            + ", ".join(
                key for key in internal.CONFIG_REQUIRED_KEYS if key not in config
            )
        )

    if not isinstance(config["project"], str):
        msg = "The 'project' key must be a string."
        raise TypeError(msg)

    if not isinstance(config["modules"], list):
        msg = "The 'modules' key must be a list."
        raise TypeError(msg)

    if not isinstance(config["experiment"], str):
        msg = "The 'experiment' key must be a string."
        raise TypeError(msg)

    # the "science_configurations" key is optional
    if "science_configurations" in config:
        if not isinstance(config["science_configurations"], list):
            msg = "The 'science_configurations' key must be a list."
            raise TypeError(msg)
        if config["science_configurations"] == []:
            msg = "The 'science_configurations' key cannot be empty."
            raise ValueError(msg)
        if not all(
            isinstance(value, dict) for value in config["science_configurations"]
        ):
            msg = (
                "Science config settings must be specified using a dictionary "
                "that is compatible with the f90nml python package."
            )
            raise TypeError(msg)

    # the "fluxsite" key is optional
    if "fluxsite" in config:
        if not isinstance(config["fluxsite"], dict):
            msg = "The 'fluxsite' key must be a dictionary."
            raise TypeError(msg)
        # the "pbs" key is optional
        if "pbs" in config["fluxsite"]:
            if not isinstance(config["fluxsite"]["pbs"], dict):
                msg = "The 'pbs' key must be a dictionary."
                raise TypeError(msg)
            # the "ncpus" key is optional
            if "ncpus" in config["fluxsite"]["pbs"] and not isinstance(
                config["fluxsite"]["pbs"]["ncpus"], int
            ):
                msg = "The 'ncpus' key must be an integer."
                raise TypeError(msg)
            # the "mem" key is optional
            if "mem" in config["fluxsite"]["pbs"] and not isinstance(
                config["fluxsite"]["pbs"]["mem"], str
            ):
                msg = "The 'mem' key must be a string."
                raise TypeError(msg)
            # the "walltime" key is optional
            if "walltime" in config["fluxsite"]["pbs"] and not isinstance(
                config["fluxsite"]["pbs"]["walltime"], str
            ):
                msg = "The 'walltime' key must be a string."
                raise TypeError(msg)
            # the "storage" key is optional
            if "storage" in config["fluxsite"]["pbs"]:
                if not isinstance(config["fluxsite"]["pbs"]["storage"], list) or any(
                    not isinstance(val, str)
                    for val in config["fluxsite"]["pbs"]["storage"]
                ):
                    msg = "The 'storage' key must be a list of strings."
                    raise TypeError(msg)
        # the "multiprocessing" key is optional
        if "multiprocessing" in config["fluxsite"] and not isinstance(
            config["fluxsite"]["multiprocessing"], bool
        ):
            msg = "The 'multiprocessing' key must be a boolean."
            raise TypeError(msg)

    valid_experiments = (
        list(internal.MEORG_EXPERIMENTS) + internal.MEORG_EXPERIMENTS["five-site-test"]
    )
    if config["experiment"] not in valid_experiments:
        msg = (
            "The 'experiment' key is invalid.\n"
            "Valid experiments are: " + ", ".join(valid_experiments)
        )
        raise ValueError(msg)

    if not isinstance(config["realisations"], list):
        msg = "The 'realisations' key must be a list."
        raise TypeError(msg)

    if config["realisations"] == []:
        msg = "The 'realisations' key cannot be empty."
        raise ValueError(msg)

    for branch_id, branch_config in enumerate(config["realisations"]):
        if not isinstance(branch_config, dict):
            msg = f"Realisation '{branch_id}' must be a dictionary object."
            raise TypeError(msg)
        if "path" not in branch_config:
            msg = f"Realisation '{branch_id}' must specify the `path` field."
            raise ValueError(msg)
        if not isinstance(branch_config["path"], str):
            msg = f"The 'path' field in realisation '{branch_id}' must be a string."
            raise TypeError(msg)
        # the "name" key is optional
        if "name" in branch_config and not isinstance(branch_config["name"], str):
            msg = f"The 'name' field in realisation '{branch_id}' must be a string."
            raise TypeError(msg)
        # the "revision" key is optional
        if "revision" in branch_config and not isinstance(
            branch_config["revision"], int
        ):
            msg = (
                f"The 'revision' field in realisation '{branch_id}' must be an "
                "integer."
            )
            raise TypeError(msg)
        # the "patch" key is optional
        if "patch" in branch_config and not isinstance(branch_config["patch"], dict):
            msg = (
                f"The 'patch' field in realisation '{branch_id}' must be a "
                "dictionary that is compatible with the f90nml python package."
            )
            raise TypeError(msg)
        # the "patch_remove" key is optional
        if "patch_remove" in branch_config and not isinstance(
            branch_config["patch_remove"], dict
        ):
            msg = (
                f"The 'patch_remove' field in realisation '{branch_id}' must be a "
                "dictionary that is compatible with the f90nml python package."
            )
            raise TypeError(msg)
        # the "build_script" key is optional
        if "build_script" in branch_config and not isinstance(
            branch_config["build_script"], str
        ):
            msg = (
                f"The 'build_script' field in realisation '{branch_id}' must be a "
                "string."
            )
            raise TypeError(msg)


def read_config(config_path: Path) -> dict:
    """Reads the config file and returns a dictionary containing the configurations."""
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    check_config(config)

    return config
