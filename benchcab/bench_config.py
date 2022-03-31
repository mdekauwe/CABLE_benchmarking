import yaml
from pathlib import Path
import os
from benchcab.set_default_paths import set_paths

def check_config(opt:dict):
    """Run some checks on the config file to ensure the data is coherent.
    check1: make sure the names in use_branches are keys in the dictionary.
    check2: make sure all required entries are listed
    """

    assert all([x in opt for x in opt["use_branches"]]), "Not all aliases listed in use_branches "\
        "were used as entries in the config file to define a CABLE branch"

    assert all([x in opt for x in ["use_branches","project","user"]]), "The config file does not "\
        "list all required entries. Those are 'use_branches', 'project','user'"

def read_config(myconfig:str):
    """Read config file for the CABLE benchmarking"""

    assert Path(myconfig).is_file(), f"{myconfig} was not found"

    with open(Path(myconfig), "r") as fin:
        opt = yaml.safe_load(fin)
    
    check_config(opt)
    return opt

def compilation_setup(envfile:str):
    """Read the environment file and load the modules and define the paths to libraries 
    depending on the machine name as needed for CABLE compilation.
    
    envfile: str, path to the environment file defining the modules to use"""

    (_, nodename, _, _, _) = os.uname()

    compilation_opt = set_paths(nodename, envfile)

    return compilation_opt

