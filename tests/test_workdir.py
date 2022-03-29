from pathlib import Path
import tempfile
import os
import yaml

from benchcab.scripts import benchtree
from benchcab.scripts import bench_config


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