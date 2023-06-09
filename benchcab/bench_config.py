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
            "The config file does not list all required entries. "
            "Those are: " + ", ".join(internal.CONFIG_REQUIRED_KEYS)
        )

    if not isinstance(config["project"], str):
        raise TypeError("The 'project' key must be a string.")

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
        if not all(
            isinstance(value, dict) for value in config["science_configurations"]
        ):
            raise TypeError(
                "Science config settings must be specified using a dictionary "
                "that is compatible with the f90nml python package."
            )

    valid_experiments = (
        list(internal.MEORG_EXPERIMENTS) + internal.MEORG_EXPERIMENTS["five-site-test"]
    )
    if config["experiment"] not in valid_experiments:
        raise ValueError(
            "The 'experiment' key is invalid.\n"
            "Valid experiments are: " + ", ".join(valid_experiments)
        )

    if not isinstance(config["realisations"], list):
        raise TypeError("The 'realisations' key must be a list.")

    if config["realisations"] == []:
        raise ValueError("The 'realisations' key cannot be empty.")

    for branch_id, branch_config in enumerate(config["realisations"]):
        if not isinstance(branch_config, dict):
            raise TypeError(f"Realisation '{branch_id}' must be a dictionary object.")
        if "path" not in branch_config:
            raise ValueError(
                f"Realisation '{branch_id}' must specify the `path` field."
            )
        if not isinstance(branch_config["path"], str):
            raise TypeError(
                f"The 'path' field in realisation '{branch_id}' must be a string."
            )
        # the "name" key is optional
        if "name" in branch_config and not isinstance(branch_config["name"], str):
            raise TypeError(
                f"The 'name' field in realisation '{branch_id}' must be a string."
            )
        # the "revision" key is optional
        if "revision" in branch_config and not isinstance(
            branch_config["revision"], int
        ):
            raise TypeError(
                f"The 'revision' field in realisation '{branch_id}' must be an "
                "integer."
            )
        # the "patch" key is optional
        if "patch" in branch_config and not isinstance(branch_config["patch"], dict):
            raise TypeError(
                f"The 'patch' field in realisation '{branch_id}' must be a "
                "dictionary that is compatible with the f90nml python package."
            )
        # the "build_script" key is optional
        if "build_script" in branch_config and not isinstance(
            branch_config["build_script"], str
        ):
            raise TypeError(
                f"The 'build_script' field in realisation '{branch_id}' must be a "
                "string."
            )


def read_config(config_path: str) -> dict:
    """Reads the config file and returns a dictionary containing the configurations."""

    with open(Path(config_path), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    check_config(config)

    for branch in config["realisations"]:
        # Add "name" key if not provided and set to base name of "path" key
        branch.setdefault("name", Path(branch["path"]).name)
        # Add "revision" key if not provided and set to default value -1, i.e. HEAD of branch
        branch.setdefault("revision", -1)
        # Add "patch" key if not provided and set to default value {}
        branch.setdefault("patch", {})
        # Add "build_script" key if not provided and set to default value ""
        branch.setdefault("build_script", "")

    # Add "science_configurations" if not provided and set to default value
    config.setdefault("science_configurations", internal.DEFAULT_SCIENCE_CONFIGURATIONS)

    return config
