"""Contains the definition of the command line interface used for `benchcab`."""

import argparse
import benchcab


def generate_parser() -> argparse.ArgumentParser:
    """Returns the instance of `argparse.ArgumentParser` used for `benchcab`."""

    # parent parser that contains the help argument
    args_help = argparse.ArgumentParser(add_help=False)
    args_help.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.'
    )

    # parent parser that contains arguments common to all subcommands
    args_subcommand = argparse.ArgumentParser(add_help=False)
    args_subcommand.add_argument(
        "-c",
        "--config",
        help="Config filename.",
        default="config.yaml"
    )

    # parent parser that contains arguments common to all run specific subcommands
    args_run_subcommand = argparse.ArgumentParser(add_help=False)
    args_run_subcommand.add_argument(
        '--no-submit',
        action='store_true',
        help="Force benchcab to execute tasks on the current compute node."
    )

    # main parser
    main_parser = argparse.ArgumentParser(
        description="benchcab is a tool for evaluation of the CABLE land surface model.",
        parents=[args_help],
        add_help=False
    )

    main_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"benchcab {benchcab.__version__}",
        help="Show program's version number and exit."
    )

    subparsers = main_parser.add_subparsers(dest='subcommand', metavar="command")

    # subcommand: 'benchcab run'
    subparsers.add_parser(
        'run',
        parents=[args_help, args_subcommand, args_run_subcommand],
        help="Run all test suites for CABLE.",
        description="""Runs all test suites for CABLE: fluxnet sites and spatial test suites. This
        command runs the full default set of tests for CABLE.""",
        add_help=False
    )

    # subcommand: 'benchcab fluxnet'
    subparsers.add_parser(
        'fluxnet',
        parents=[args_help, args_subcommand, args_run_subcommand],
        help="Run the fluxnet test suite for CABLE.",
        description="""Runs the default fluxnet test suite for CABLE. This command is the
        equivalent of running 'benchcab checkout', 'benchcab build', 'benchcab
        fluxnet-setup-work-dir', and 'benchcab fluxnet-run-tasks' sequentially.""",
        add_help=False
    )

    # subcommand: 'benchcab checkout'
    subparsers.add_parser(
        'checkout',
        parents=[args_help, args_subcommand],
        help="Run the checkout step in the benchmarking workflow.",
        description="""Checkout CABLE repositories specified in the config file and the CABLE-AUX
        repository.""",
        add_help=False
    )

    # subcommand: 'benchcab build'
    subparsers.add_parser(
        'build',
        parents=[args_help, args_subcommand],
        help="Run the build step in the benchmarking workflow.",
        description="""Build the CABLE offline executable for each repository specified in the
        config file.""",
        add_help=False
    )

    # subcommand: 'benchcab fluxnet-setup-work-dir'
    subparsers.add_parser(
        'fluxnet-setup-work-dir',
        parents=[args_help, args_subcommand],
        help="Run the work directory setup step of the fluxnet command.",
        description="""Generates the benchcab site/run directory tree in the current working
        directory so that tasks can be run.""",
        add_help=False
    )

    # subcommand: 'benchcab fluxnet-run-tasks'
    subparsers.add_parser(
        'fluxnet-run-tasks',
        parents=[args_help, args_subcommand, args_run_subcommand],
        help="Run the fluxnet tasks of the main fluxnet command.",
        description="""Runs the fluxnet tasks for the fluxnet test suite. By default, this
        command generates a PBS job script and submits it to the queue.""",
        add_help=False
    )

    # subcommand: 'benchcab spatial'
    subparsers.add_parser(
        'spatial',
        parents=[args_help, args_subcommand],
        help="Run the spatial tests only.",
        description="""Runs the default spatial test suite for CABLE.""",
        add_help=False
    )

    return main_parser
