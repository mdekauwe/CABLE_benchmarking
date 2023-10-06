"""A module containing functions for generating the directory structure
used for `benchcab`."""

from pathlib import Path
import shutil

from benchcab import internal
from benchcab.utils.fs import mkdir, chdir


def clean_directory_tree(root_dir=internal.CWD):
    """Remove pre-existing directories in current working directory."""
    src_dir = Path(root_dir, internal.SRC_DIR)
    if src_dir.exists():
        shutil.rmtree(src_dir)

    run_dir = Path(root_dir, internal.RUN_DIR)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def setup_fluxsite_directory_tree(root_dir=internal.CWD, verbose=False):
    """Generate the directory structure used by `benchcab`.

    Parameters
    ----------
    root_dir : Path, optional
        The root directory to add to relative paths, by default internal.CWD
    verbose : bool, default False
        Additional level of logging if True
    """

    # Create the list of directories.
    fluxsite_paths = [
        # Fluxsite run directory
        internal.FLUXSITE_RUN_DIR,
        # Fluxsite log directory
        internal.FLUXSITE_LOG_DIR,
        # Fluxsite output directory
        internal.FLUXSITE_OUTPUT_DIR,
        # Fluxsite tasks directory
        internal.FLUXSITE_TASKS_DIR,
        # Fluxsite analysis directory
        internal.FLUXSITE_ANALYSIS_DIR,
        # Fluxsite bit-wise comparison directory
        internal.FLUXSITE_BITWISE_CMP_DIR,
    ]

    with chdir(root_dir):
        for path in fluxsite_paths:
            mkdir(path, verbose=verbose, parents=True, exist_ok=True)
