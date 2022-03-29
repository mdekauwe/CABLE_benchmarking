import pytest
import yaml

@pytest.fixture
def testconfig():
    # Test config
    conf = {
        "branches":{ 
            "branch1":{
                "name": "v3.0-YP-changes",
                "trunk": False,
                "share_branch": False
                },
            "branch2":{
                "name": "trunk",
                "trunk": True,
                "share_branch": False
                },
            }
        }
    return conf

@pytest.fixture
def create_testconfig(testconfig, tmp_path):

    with open(tmp_path/"config.yaml", "w") as fout:
        yaml.dump(testconfig,fout)

    return tmp_path
