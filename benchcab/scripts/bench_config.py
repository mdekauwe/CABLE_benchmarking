import yaml
from pathlib import Path

def read_config(myconfig:str):
    """Read config file for the CABLE benchmarking"""

    assert Path(myconfig).is_file(), f"{myconfig} was not found"

    with open(Path(myconfig), "r") as fin:
        opt = yaml.safe_load(fin)
    
    return opt