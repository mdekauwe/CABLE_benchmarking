#!/usr/bin/env python

"""Contains the main program entry point for `benchcab`."""

import argparse
import sys

from benchcab.job_script import create_job_script, submit_job
from benchcab.bench_config import read_config
from benchcab.benchtree import setup_fluxnet_directory_tree, setup_src_dir
from benchcab.build_cable import build_cable_offline
from benchcab.get_cable import checkout_cable, checkout_cable_auxiliary, archive_rev_number
from benchcab.internal import validate_environment, get_met_sites, MULTIPROCESS
from benchcab.task import get_fluxnet_tasks, Task
from benchcab.cli import generate_parser
from benchcab.run_cable_site import run_tasks, run_tasks_in_parallel


def benchcab_checkout(config: dict):
    """Endpoint for `benchcab checkout`."""
    setup_src_dir()
    for branch in config['realisations'].values():
        checkout_cable(branch_config=branch, user=config['user'])
    checkout_cable_auxiliary()
    archive_rev_number()


def benchcab_build(config: dict):
    """Endpoint for `benchcab build`."""
    for branch in config['realisations'].values():
        build_cable_offline(branch['name'], config['modules'])


def benchcab_fluxnet_setup_work_directory(tasks: list[Task]):
    """Endpoint for `benchcab fluxnet-setup-work-dir`."""
    setup_fluxnet_directory_tree(fluxnet_tasks=tasks)
    for task in tasks:
        task.setup_task()


def benchcab_fluxnet_run_tasks(args: argparse.Namespace, config: dict, tasks: list[Task]):
    """Endpoint for `benchcab fluxnet-run-tasks [--no-submit]`."""
    if args.no_submit:
        if MULTIPROCESS:
            run_tasks_in_parallel(tasks)
        else:
            run_tasks(tasks)
    else:
        create_job_script(
            project=config['project'],
            user=config['user'],
            config_path=args.config,
            modules=config['modules']
        )
        submit_job()


def benchcab_fluxnet(args: argparse.Namespace, config: dict, tasks: list[Task]):
    """Endpoint for `benchcab fluxnet [--no-submit]`."""
    benchcab_checkout(config)
    benchcab_build(config)
    benchcab_fluxnet_setup_work_directory(tasks)
    benchcab_fluxnet_run_tasks(args, config, tasks)


def main():
    """Main program entry point for `benchcab`.

    This is required for setup.py entry_points
    """

    args = generate_parser().parse_args(sys.argv[1:] if sys.argv[1:] else ['-h'])
    config = read_config(args.config)
    validate_environment(project=config['project'], modules=config['modules'])

    if args.subcommand == 'checkout':
        benchcab_checkout(config)
        return

    if args.subcommand == 'build':
        benchcab_build(config)
        return

    if args.subcommand == 'fluxnet':
        tasks = get_fluxnet_tasks(
            realisations=config["realisations"],
            science_config=config['science_configurations'],
            met_sites=get_met_sites(config['experiment'])
        )
        benchcab_fluxnet(args, config, tasks)
        return

    if args.subcommand == 'fluxnet-setup-work-dir':
        tasks = get_fluxnet_tasks(
            realisations=config["realisations"],
            science_config=config['science_configurations'],
            met_sites=get_met_sites(config['experiment'])
        )
        benchcab_fluxnet_setup_work_directory(tasks)
        return

    if args.subcommand == 'fluxnet-run-tasks':
        tasks = get_fluxnet_tasks(
            realisations=config["realisations"],
            science_config=config['science_configurations'],
            met_sites=get_met_sites(config['experiment'])
        )
        benchcab_fluxnet_run_tasks(args, config, tasks)
        return

    if args.subcommand == 'spatial':
        print("Warning: spatial tests not yet implemented")
        return


if __name__ == "__main__":
    main()
