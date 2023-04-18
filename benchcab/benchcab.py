#!/usr/bin/env python

"""Contains the main program entry point for `benchcab`."""

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


class Benchcab():
    """A class that represents the `benchcab` application."""

    def __init__(self) -> None:
        self.args = generate_parser().parse_args(sys.argv[1:] if sys.argv[1:] else ['-h'])
        self.config = read_config(self.args.config)
        self.tasks: list[Task] = []  # initialise fluxnet tasks lazily
        validate_environment(project=self.config['project'], modules=self.config['modules'])

    def _initialise_tasks(self) -> list[Task]:
        """A helper method that initialises and returns the `tasks` attribute."""
        self.tasks = get_fluxnet_tasks(
            realisations=self.config['realisations'],
            science_config=self.config['science_configurations'],
            met_sites=get_met_sites(self.config['experiment'])
        )
        return self.tasks

    def checkout(self):
        """Endpoint for `benchcab checkout`."""
        setup_src_dir()
        for branch in self.config['realisations'].values():
            checkout_cable(branch_config=branch, user=self.config['user'])
        checkout_cable_auxiliary()
        archive_rev_number()
        return self

    def build(self):
        """Endpoint for `benchcab build`."""
        for branch in self.config['realisations'].values():
            build_cable_offline(branch['name'], self.config['modules'])
        return self

    def fluxnet_setup_work_directory(self):
        """Endpoint for `benchcab fluxnet-setup-work-dir`."""
        tasks = self.tasks if self.tasks else self._initialise_tasks()
        setup_fluxnet_directory_tree(fluxnet_tasks=tasks)
        for task in tasks:
            task.setup_task()
        return self

    def fluxnet_run_tasks(self):
        """Endpoint for `benchcab fluxnet-run-tasks`."""
        if self.args.no_submit:
            tasks = self.tasks if self.tasks else self._initialise_tasks()
            if MULTIPROCESS:
                run_tasks_in_parallel(tasks)
            else:
                run_tasks(tasks)
        else:
            create_job_script(
                project=self.config['project'],
                user=self.config['user'],
                config_path=self.args.config,
                modules=self.config['modules']
            )
            submit_job()
        return self

    def fluxnet(self):
        """Endpoint for `benchcab fluxnet`."""
        self.checkout() \
            .build() \
            .fluxnet_setup_work_directory() \
            .fluxnet_run_tasks()
        return self

    def spatial(self):
        """Endpoint for `benchcab spatial`."""
        return self

    def run(self):
        """Endpoint for `benchcab run`."""
        self.fluxnet() \
            .spatial()
        return self

    def main(self):
        """Main function for `benchcab`."""

        if self.args.subcommand == 'run':
            self.run()

        if self.args.subcommand == 'checkout':
            self.checkout()

        if self.args.subcommand == 'build':
            self.build()

        if self.args.subcommand == 'fluxnet':
            self.fluxnet()

        if self.args.subcommand == 'fluxnet-setup-work-dir':
            self.fluxnet_setup_work_directory()

        if self.args.subcommand == 'fluxnet-run-tasks':
            self.fluxnet_run_tasks()

        if self.args.subcommand == 'spatial':
            self.spatial()


def main():
    """Main program entry point for `benchcab`.

    This is required for setup.py entry_points
    """

    app = Benchcab()
    app.main()


if __name__ == "__main__":
    main()
