#!/usr/bin/env python
import yaml
from pathlib import Path
import tempfile
import os
import pytest

from benchcab import benchcab

mydir = Path.cwd()

def test_run_sites(create_testconfig):

    os.chdir(create_testconfig)
    mess = "Running the single sites tests "
    assert benchcab.main_parse_args(["-f"]) == mess

    os.chdir(mydir)

def test_run_spatial(create_testconfig):

    os.chdir(create_testconfig)
    mess = "Running the spatial tests "
    assert benchcab.main_parse_args(["-w"]) == mess

    os.chdir(mydir)


def test_run_all(create_testconfig):

    os.chdir(create_testconfig)
    mess = "Running the single sites tests "+"Running the spatial tests "
    assert benchcab.main_parse_args([]) == mess
    
    os.chdir(mydir)

