"""`pytest` tests for cli.py"""

import pytest
from benchcab.cli import generate_parser


def test_cli_parser():
    """Tests for `generate_parser()`."""

    parser = generate_parser()

    # Success case: default benchcab command
    res = vars(parser.parse_args(["run"]))
    assert res == {
        "subcommand": "run",
        "config": "config.yaml",
        "no_submit": False,
        "verbose": False,
    }

    # Success case: default checkout command
    res = vars(parser.parse_args(["checkout"]))
    assert res == {"subcommand": "checkout", "config": "config.yaml", "verbose": False}

    # Success case: default build command
    res = vars(parser.parse_args(["build"]))
    assert res == {"subcommand": "build", "config": "config.yaml", "verbose": False}

    # Success case: default fluxnet command
    res = vars(parser.parse_args(["fluxnet"]))
    assert res == {
        "subcommand": "fluxnet",
        "config": "config.yaml",
        "no_submit": False,
        "verbose": False,
    }

    # Success case: default fluxnet-setup-work-dir command
    res = vars(parser.parse_args(["fluxnet-setup-work-dir"]))
    assert res == {
        "subcommand": "fluxnet-setup-work-dir",
        "config": "config.yaml",
        "verbose": False,
    }

    # Success case: default fluxnet run-tasks command
    res = vars(parser.parse_args(["fluxnet-run-tasks"]))
    assert res == {
        "subcommand": "fluxnet-run-tasks",
        "config": "config.yaml",
        "verbose": False,
    }

    # Success case: default fluxnet-bitwise-cmp command
    res = vars(parser.parse_args(["fluxnet-bitwise-cmp"]))
    assert res == {
        "subcommand": "fluxnet-bitwise-cmp",
        "config": "config.yaml",
        "verbose": False,
    }

    # Success case: default spatial command
    res = vars(parser.parse_args(["spatial"]))
    assert res == {
        "subcommand": "spatial",
        "config": "config.yaml",
        "verbose": False,
    }

    # Failure case: pass --no-submit to a non 'run' command
    with pytest.raises(SystemExit):
        parser.parse_args(["fluxnet-setup-work-dir", "--no-submit"])
