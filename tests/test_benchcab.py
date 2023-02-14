#!/usr/bin/env python
import pytest
pytest.skip(allow_module_level=True)

import yaml
from pathlib import Path
import tempfile
import os

from benchcab import benchcab
from benchcab import build_cable
from tests.test_workdir import checkout_branch

mydir = Path.cwd()

def test_run_sites(create_testconfig):

    os.chdir(create_testconfig[0])
    mess = "Running the single sites tests "
    assert benchcab.main_parse_args(["-f"]) == mess

    os.chdir(mydir)

def test_run_spatial(create_testconfig):

    os.chdir(create_testconfig[0])
    mess = "Running the spatial tests "
    assert benchcab.main_parse_args(["-w"]) == mess

    os.chdir(mydir)


def test_run_all(create_testconfig):

    os.chdir(create_testconfig[0])
    mess = "Running the single sites tests "+"Running the spatial tests "
    assert benchcab.main_parse_args([]) == mess
    
    os.chdir(mydir)

# def test_compilation(create_testconfig):

#     os.chdir(create_testconfig)

#     checkout_branch("user", create_testconfig)
#     B = build_cable.BuildCable(
#         src_dir=benchdirs.src_dir,
#         ModToLoad=opt["modules"],
#         **compilation_opt,
#         mpi=True,
#         )
#     B.main(repo_name=branch1["name"])



