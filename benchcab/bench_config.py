"""
A module containing all *_config() functions.

"""

from pathlib import Path
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

    if not isinstance(config["realisations"], list):
        raise TypeError("The 'realisations' key must be a list.")

    if config["realisations"] == []:
        raise ValueError("The 'realisations' key cannot be empty.")

    if any(not isinstance(branch, dict) for branch in config["realisations"]):
        raise TypeError("The 'realisations' key must contain dictionary objects.")

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
        if not isinstance(config["science_configurations"], list):
            raise TypeError("The 'science_configurations' key must be a list.")
        if config["science_configurations"] == []:
            raise ValueError("The 'science_configurations' key cannot be empty.")
        if not all(isinstance(value, dict) for value in config["science_configurations"]):
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

    for branch_id, branch_config in enumerate(config['realisations']):
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


def read_config(config_path: str) -> dict:
    """Reads the config file and returns a dictionary containing the configurations."""

    with open(Path(config_path), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    check_config(config)

    for branch in config['realisations']:
        # Add "revision" key if not provided and set to default value -1, i.e. HEAD of branch
        branch.setdefault('revision', -1)
        # Add "patch" key if not provided and set to default value {}
        branch.setdefault('patch', {})

    # Add "science_configurations" if not provided and set to default value
    config.setdefault("science_configurations", DEFAULT_SCIENCE_CONFIGURATIONS)

    return config
