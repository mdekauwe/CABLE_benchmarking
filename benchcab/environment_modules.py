"""Contains a wrapper around the environment modules API."""

import sys

sys.path.append("/opt/Modules/v4.3.0/init")
try:
    from python import module  # pylint: disable=import-error
except ImportError:
    print(
        "Environment modules error: unable to import "
        "initialization script for python."
    )
    # Note: cannot re-raise exception here as this will break pytest
    # when running pytest locally (outside of Gadi)


class EnvironmentModulesError(Exception):
    """Custom exception class for environment modules errors."""


def module_is_avail(*args: str):
    """Wrapper around `module is-avail modulefile...`"""
    return module("is-avail", *args)


def module_is_loaded(*args: str):
    """Wrapper around `module is-loaded modulefile...`"""
    return module("is-loaded", *args)


def module_load(*args: str):
    """Wrapper around `module load modulefile...`"""
    if not module("load", *args):
        raise EnvironmentModulesError("Failed to load modules: " + " ".join(args))


def module_unload(*args: str):
    """Wrapper around `module unload modulefile...`"""
    if not module("unload", *args):
        raise EnvironmentModulesError("Failed to unload modules: " + " ".join(args))
