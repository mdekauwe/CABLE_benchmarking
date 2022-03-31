import pytest
import os
import yaml
from pathlib import Path

@pytest.fixture
def testconfig():
    # Test config
    conf = {
        "use_branches":["user_branch","trunk"],
        "user_branch":{
            "name": "v3.0-YP-changes",
            "trunk": False,
            "share_branch": False,
            },
        "trunk":{
            "name": "trunk",
            "trunk": True,
            "share_branch": False,
            },
        "share":{
            "name": "integration",
            "trunk": False,
            "share_branch": True,
            },
        "user":os.environ["USER"],
        "project":os.environ["PROJECT"],
        "modules":[
            "intel-compiler/2021.1.1",
            "openmpi/4.1.0",
            "netcdf/4.7.4",
        ],
        }
    return conf

@pytest.fixture
def create_testconfig(testconfig, tmp_path):

    with open(tmp_path/"config.yaml", "w") as fout:
        yaml.dump(testconfig,fout)

    return tmp_path
