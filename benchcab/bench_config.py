"""
A module containing all *_config() functions.

"""

from pathlib import Path
import re
import yaml


def check_config(config: dict):
    """Performs input validation on config file.

    If the config is invalid, an exception is raised. Otherwise, do nothing.
    """

    required_keys = ['realisations', 'project', 'user', 'modules']
    if any(key not in config for key in required_keys):
        raise ValueError(
            "The config file does not list all required entries. "
            "Those are 'realisations', 'project', 'user', 'modules'"
        )

    if len(config["realisations"]) != 2:
        raise ValueError("You need to list 2 branches in 'realisations'")

    for branch_id, branch_config in config['realisations'].items():
        required_keys = ["name", "trunk", "share_branch"]
        if any(key not in branch_config for key in required_keys):
            raise ValueError(
                f"Realisation '{branch_id}' does not list all required "
                "entries. Those are 'name', 'trunk', 'share_branch'."
            )
        if not isinstance(branch_config["name"], str):
            raise TypeError(
                f"The 'name' field in realisation '{branch_id}' must be a "
                "string."
            )
        # the "revision" key is optional
        if "revision" in branch_config and not isinstance(branch_config["revision"], int):
            raise TypeError(
                f"The 'revision' field in realisation '{branch_id}' must be an "
                "integer."
            )
        if not isinstance(branch_config["trunk"], bool):
            raise TypeError(
                f"The 'trunk' field in realisation '{branch_id}' must be a "
                "boolean."
            )
        if not isinstance(branch_config["share_branch"], bool):
            raise TypeError(
                f"The 'share_branch' field in realisation '{branch_id}' must be a "
                "boolean."
            )


def check_science_config(science_config: dict):
    """Performs input validation on science config file.

    If the science config is invalid, an exception is raised. Otherwise, do nothing.
    """

    if any(re.fullmatch("sci[0-9]+", key) is None for key in science_config):
        raise ValueError(
            "Science config keys must be in the format: "
            "sci<count> where count = 0, 1, 2, ..."
        )


def read_config(config_path: str) -> dict:
    """Reads the config file and returns a dictionary containing the configurations."""

    with open(Path(config_path), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    check_config(config)

    # Add "revision" to each branch description if not provided with default value -1,
    # i.e. HEAD of branch
    for branch in config['realisations'].values():
        branch.setdefault('revision', -1)

    # Add a "met_subset" key set to empty list if not found in config.yaml file.
    config.setdefault("met_subset", [])

    return config


def read_science_config(science_config_path) -> dict:
    """Reads the science config file and returns a dictionary containing the configurations."""

    with open(science_config_path, "r", encoding="utf-8") as file:
        science_config = yaml.safe_load(file)

    check_science_config(science_config)

    return science_config
