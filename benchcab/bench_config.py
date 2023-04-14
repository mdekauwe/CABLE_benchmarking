"""
A module containing all *_config() functions.

"""

from pathlib import Path
import re
import yaml

from benchcab.internal import MEORG_EXPERIMENTS, DEFAULT_SCIENCE_CONFIGURATIONS


def check_config(config: dict):
    """Performs input validation on config file.

    If the config is invalid, an exception is raised. Otherwise, do nothing.
    """

    required_keys = ['realisations', 'project', 'user', 'modules', 'experiment']
    if any(key not in config for key in required_keys):
        raise ValueError(
            "The config file does not list all required entries. "
            "Those are 'realisations', 'project', 'user', 'modules'"
        )

    if not isinstance(config["realisations"], dict):
        raise TypeError("The 'realisations' key must be a dictionary.")

    if not isinstance(config["project"], str):
        raise TypeError("The 'project' key must be a string.")

    if not isinstance(config["user"], str):
        raise TypeError("The 'user' key must be a string.")

    if not isinstance(config["modules"], list):
        raise TypeError("The 'modules' key must be a list.")

    if not isinstance(config["experiment"], str):
        raise TypeError("The 'experiment' key must be a string.")

    # the "science_configurations" key is optional
    if "science_configurations" in config:
        if not isinstance(config["science_configurations"], dict):
            raise TypeError("The 'science_configurations' key must be a dictionary.")
        if config["science_configurations"] == {}:
            raise ValueError("The 'science_configurations' key cannot be empty.")
        if not all(re.fullmatch("sci[0-9]+", key) for key in config["science_configurations"]):
            raise ValueError(
                "Science config keys must be in the format: "
                "sci<count> where count = 0, 1, 2, ..."
            )
        if not all(isinstance(value, dict) for value in config["science_configurations"].values()):
            raise TypeError(
                "Science config settings must be specified using a dictionary "
                "that is compatible with the f90nml python package."
            )

    valid_experiments = list(MEORG_EXPERIMENTS) + MEORG_EXPERIMENTS["five-site-test"]
    if config["experiment"] not in valid_experiments:
        raise ValueError(
            "The 'experiment' key is invalid.\n"
            "Valid experiments are: " ", ".join(valid_experiments)
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
        # the "patch" key is optional
        if "patch" in branch_config and not isinstance(branch_config["patch"], dict):
            raise TypeError(
                f"The 'patch' field in realisation '{branch_id}' must be a "
                "dictionary that is compatible with the f90nml python package."
            )

        # the "build_script" key is optional
        if "build_script" in branch_config and not isinstance(branch_config["build_script"], str):
            raise TypeError(
                f"The 'build_script' field in realisation '{branch_id}' must be a "
                "string."
            )


def get_science_config_id(key: str) -> str:
    """Get ID from science config key."""
    match = re.fullmatch("sci([0-9]+)", key)
    if not match:
        raise ValueError(
            "Science config keys must be in the format: "
            "sci<count> where count = 0, 1, 2, ..."
        )
    return match.group(1)


def read_config(config_path: str) -> dict:
    """Reads the config file and returns a dictionary containing the configurations."""

    with open(Path(config_path), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    check_config(config)

    for branch in config['realisations'].values():
        # Add "revision" key if not provided and set to default value -1, i.e. HEAD of branch
        branch.setdefault('revision', -1)
        # Add "patch" key if not provided and set to default value {}
        branch.setdefault('patch', {})
        # Add "build_script" key if not provided and set to default value ""
        branch.setdefault('build_script', "")

    # Add "science_configurations" if not provided and set to default value
    if "science_configurations" not in config:
        config["science_configurations"] = DEFAULT_SCIENCE_CONFIGURATIONS

    return config
