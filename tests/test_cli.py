"""`pytest` tests for cli.py"""

import pytest
from benchcab.cli import generate_parser


def test_cli_parser():
    """Tests for `generate_parser()`."""

    parser = generate_parser()

    # Success case: default benchcab command
    res = vars(parser.parse_args(['run']))
    assert res == {'subcommand': 'run', 'config': 'config.yaml', 'no_submit': False}

    # Success case: default benchcab command with a user supplied config
    res = vars(parser.parse_args(['run', '--config=my_config.yaml']))
    assert res == {'subcommand': 'run', 'config': 'my_config.yaml', 'no_submit': False}

    # Success case: default benchcab command with --no-submit enabled
    res = vars(parser.parse_args(['run', '--no-submit']))
    assert res == {'subcommand': 'run', 'config': 'config.yaml', 'no_submit': True}

    # Success case: default benchcab command with a user supplied config with --no-submit enabled
    res = vars(parser.parse_args(['run', '--config=my_config.yaml', '--no-submit']))
    assert res == {'subcommand': 'run', 'config': 'my_config.yaml', 'no_submit': True}

    # Success case: default checkout command
    res = vars(parser.parse_args(['checkout']))
    assert res == {'subcommand': 'checkout', 'config': 'config.yaml'}

    # Success case: default checkout command with a user supplied config
    res = vars(parser.parse_args(['checkout', '--config=my_config.yaml']))
    assert res == {'subcommand': 'checkout', 'config': 'my_config.yaml'}

    # Success case: default build command
    res = vars(parser.parse_args(['build']))
    assert res == {'subcommand': 'build', 'config': 'config.yaml'}

    # Success case: default build command with a user supplied config
    res = vars(parser.parse_args(['build', '--config=my_config.yaml']))
    assert res == {'subcommand': 'build', 'config': 'my_config.yaml'}

    # Success case: default fluxnet command
    res = vars(parser.parse_args(['fluxnet']))
    assert res == {
        'subcommand': 'fluxnet',
        'config': 'config.yaml',
        'no_submit': False,
    }

    # Success case: default fluxnet command with a user supplied config
    res = vars(parser.parse_args(['fluxnet', '--config=my_config.yaml']))
    assert res == {
        'subcommand': 'fluxnet',
        'config': 'my_config.yaml',
        'no_submit': False,
    }

    # Success case: default fluxnet command with --no-submit enabled
    res = vars(parser.parse_args(['fluxnet', '--no-submit']))
    assert res == {
        'subcommand': 'fluxnet',
        'config': 'config.yaml',
        'no_submit': True,
    }

    # Success case: default fluxnet command with a user supplied config with --no-submit enabled
    res = vars(parser.parse_args(['fluxnet', '--config=my_config.yaml', '--no-submit']))
    assert res == {
        'subcommand': 'fluxnet',
        'config': 'my_config.yaml',
        'no_submit': True,
    }

    # Success case: default fluxnet-setup-work-dir command
    res = vars(parser.parse_args(['fluxnet-setup-work-dir']))
    assert res == {
        'subcommand': 'fluxnet-setup-work-dir',
        'config': 'config.yaml',
    }

    # Success case: default fluxnet setup-work-dir command with a user supplied config
    res = vars(parser.parse_args(['fluxnet-setup-work-dir', '--config=my_config.yaml']))
    assert res == {
        'subcommand': 'fluxnet-setup-work-dir',
        'config': 'my_config.yaml',
    }

    # Success case: default fluxnet run-tasks command
    res = vars(parser.parse_args(['fluxnet-run-tasks']))
    assert res == {
        'subcommand': 'fluxnet-run-tasks',
        'config': 'config.yaml',
        'no_submit': False,
    }

    # Success case: default fluxnet run-tasks command with a user supplied config
    res = vars(parser.parse_args(['fluxnet-run-tasks', '--config=my_config.yaml']))
    assert res == {
        'subcommand': 'fluxnet-run-tasks',
        'config': 'my_config.yaml',
        'no_submit': False,
    }

    # Success case: default fluxnet run-tasks command with --no-submit enabled
    res = vars(parser.parse_args(['fluxnet-run-tasks', '--no-submit']))
    assert res == {
        'subcommand': 'fluxnet-run-tasks',
        'config': 'config.yaml',
        'no_submit': True,
    }

    # Success case: default fluxnet run-tasks command with a user supplied config with --no-submit
    # enabled
    res = vars(parser.parse_args(['fluxnet-run-tasks', '--config=my_config.yaml', '--no-submit']))
    assert res == {
        'subcommand': 'fluxnet-run-tasks',
        'config': 'my_config.yaml',
        'no_submit': True,
    }

    # Success case: default spatial command
    res = vars(parser.parse_args(['spatial']))
    assert res == {
        'subcommand': 'spatial',
        'config': 'config.yaml',
    }

    # Success case: default spatial command with a user supplied config path
    res = vars(parser.parse_args(['spatial', '--config=my_config.yaml']))
    assert res == {
        'subcommand': 'spatial',
        'config': 'my_config.yaml',
    }

    # Failure case: pass --no-submit to a non 'run' command
    with pytest.raises(SystemExit):
        parser.parse_args(['fluxnet-setup-work-dir', '--no-submit'])
