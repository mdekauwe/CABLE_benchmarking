from pathlib import Path
import tempfile
import os
import yaml

from benchcab import benchtree
from benchcab import bench_config
from benchcab import get_cable

def checkout_branch(branch_type:str, locdir:str):

    os.chdir(locdir)
    tb = benchtree.BenchTree(Path(locdir))
    tb.create_minbenchtree()

    # Get the branch information from the testconfig
    opt = bench_config.read_config("config.yaml")

    # Check if the branch_type exists in file?
    locbranch = opt[branch_type]
    tr = get_cable.GetCable(src_dir=tb.src_dir, user=opt["user"])
    tr.main(**locbranch)

    assert Path(f"src/{locbranch['name']}").is_dir(), "Directory does not exist"
    assert len(list(Path(f"src/{locbranch['name']}").iterdir())) > 0, "Directory is empty"


def test_create_minbenchtree(create_testconfig):
    """Test the min. directory tree is created"""

    td = create_testconfig
    # Get into the temporary directory to test creating the directory structure
    os.chdir(td)

    tb = benchtree.BenchTree(Path(td))
    tb.create_minbenchtree()

    paths_to_create=[
        (td/"src").is_dir(),
        (td/"runs").is_dir(),
    ]
    assert all(paths_to_create)
    
def test_read_config(create_testconfig, testconfig):
    
    os.chdir(create_testconfig)
    opt = bench_config.read_config("config.yaml")

    assert opt == testconfig

def test_checkout_trunk(create_testconfig):

    checkout_branch("trunk", create_testconfig)

def test_checkout_user(create_testconfig):

    checkout_branch("user_branch", create_testconfig)
 
def test_checkout_share(create_testconfig):

    checkout_branch("share", create_testconfig)


