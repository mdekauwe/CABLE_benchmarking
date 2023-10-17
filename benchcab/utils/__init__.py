"""Top-level utilities."""
import pkgutil
import json
import yaml
import os
from importlib import resources
from pathlib import Path


# List of one-argument decoding functions.
PACKAGE_DATA_DECODERS = dict(
    json=json.loads,
    yml=yaml.safe_load
)


def get_installed_root() -> Path:
    """Get the installed root of the benchcab installation.

    Returns
    -------
    Path
        Path to the installed root.
    """
    return Path(resources.files('benchcab'))


def load_package_data(filename: str) -> dict:
    """Load data out of the installed package data directory.

    Parameters
    ----------
    filename : str
        Filename of the file to load out of the data directory.
    """
    # Work out the encoding of requested file.
    ext = filename.split('.')[-1]

    # Alias yaml and yml.
    ext = ext if ext != 'yaml' else 'yml'

    # Make sure it is one of the supported types.
    assert ext in PACKAGE_DATA_DECODERS.keys()

    # Extract from the installations data directory.
    raw = pkgutil.get_data('benchcab', os.path.join('data', filename)).decode('utf-8')

    # Decode and return.
    return PACKAGE_DATA_DECODERS[ext](raw)