#!/usr/bin/env python
import yaml
from pathlib import Path
import tempfile
import os

from benchcab.cli import benchcab

mydir = Path.cwd()

def test_run_sites():

    # Need to run from a test directory
    with tempfile.TemporaryDirectory() as td:
        os.chdir(td)
        mess = "Running the single sites tests "
        assert benchcab.main_parse_args(["-f"]) == mess
        os.chdir(mydir)

def test_run_spatial():

    # Need to run from a test directory
    with tempfile.TemporaryDirectory() as td:
        os.chdir(td)
        mess = "Running the spatial tests "
        assert benchcab.main_parse_args(["-w"]) == mess
        os.chdir(mydir)


def test_run_all():

    # Need to run from a test directory
    with tempfile.TemporaryDirectory() as td:
        os.chdir(td)
        mess = "Running the single sites tests "+"Running the spatial tests "
        assert benchcab.main_parse_args([]) == mess
        os.chdir(mydir)
