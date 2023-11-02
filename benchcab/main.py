"""Main entry point for `benchcab`."""

import shutil
import sys

from benchcab.benchcab import Benchcab
from benchcab.cli import generate_parser


def parse_and_dispatch(parser):
    """Parse arguments for the script and dispatch to the correct function.

    Args:
    ----
    parser : argparse.ArgumentParser
        Parser object.
    """
    args = vars(parser.parse_args(sys.argv[1:] if sys.argv[1:] else ["-h"]))
    func = args.pop("func")
    func(**args)


def main():
    """Main program entry point for `benchcab`.

    This is required for setup.py entry_points
    """
    app = Benchcab(benchcab_exe_path=shutil.which(sys.argv[0]))
    parser = generate_parser(app)
    parse_and_dispatch(parser)


if __name__ == "__main__":
    main()
