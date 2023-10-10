"""A module containing functions for generating the directory structure
used for `benchcab`."""

import shutil

from benchcab import internal
from benchcab.utils.fs import mkdir


def clean_directory_tree():
    """Remove pre-existing directories in current working directory."""
    if internal.SRC_DIR.exists():
        shutil.rmtree(internal.SRC_DIR)

    if internal.RUN_DIR.exists():
        shutil.rmtree(internal.RUN_DIR)


def setup_fluxsite_directory_tree(verbose=False):
    """Generate the directory structure used by `benchcab`.

    Parameters
    ----------
    verbose : bool, default False
        Additional level of logging if True
    """

    for path in internal.FLUXSITE_DIRS.values():
        mkdir(path, verbose=verbose, parents=True, exist_ok=True)
