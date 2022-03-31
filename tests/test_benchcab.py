#!/usr/bin/env python
import yaml
from pathlib import Path
import tempfile
import os
import pytest

from benchcab import benchcab

mydir = Path.cwd()

def testenv():
    # Test environment file
    lines = "intel-compiler/2021.1.1\n"
    lines += "openmpi/4.1.0\n"
    lines += "netcdf/4.7.4\n"

    print(Path.cwd())
    with open(f"./gadi_env.sh","w") as fout:
        fout.write(lines)

def test_run_sites(create_testconfig):

    os.chdir(create_testconfig)
    # Create test environment file
    testenv()
    mess = "Running the single sites tests "
    assert benchcab.main_parse_args(["-f"]) == mess

    os.chdir(mydir)

def test_run_spatial(create_testconfig):

    os.chdir(create_testconfig)
    # Create test environment file
    testenv()
    mess = "Running the spatial tests "
    assert benchcab.main_parse_args(["-w"]) == mess

    os.chdir(mydir)


def test_run_all(create_testconfig):

    os.chdir(create_testconfig)
    # Create test environment file
    testenv()
    mess = "Running the single sites tests "+"Running the spatial tests "
    assert benchcab.main_parse_args([]) == mess
    
    os.chdir(mydir)

