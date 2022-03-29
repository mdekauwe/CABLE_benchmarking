#!/usr/bin/env python
import yaml
from pathlib import Path
import os

from benchcab.cli import benchcab

def test_run_sites():

    mess = "Running the single sites tests "
    assert benchcab.main_parse_args(["-f"]) == mess

def test_run_spatial():

    mess = "Running the spatial tests "
    assert benchcab.main_parse_args(["-s"]) == mess

def test_run_all():

    mess = "Running the single sites tests "+"Running the spatial tests "
    assert benchcab.main_parse_args([]) == mess

