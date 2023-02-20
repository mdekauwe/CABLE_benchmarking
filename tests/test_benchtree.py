"""`pytest` tests for benchtree.py"""

from pathlib import Path


from tests.common import make_barebones_config, make_barbones_science_config
from benchcab.benchtree import setup_fluxnet_directory_tree, clean_directory_tree

# Here we use the tmp_path fixture provided by pytest to
# run tests using a temporary directory.


def test_setup_directory_tree(tmp_path):
    """Tests for `setup_fluxnet_directory_tree()`."""

    # Success case: generate fluxnet directory structure
    config = make_barebones_config()
    science_config = make_barbones_science_config()
    branch_names = [config[branch_alias]["name"] for branch_alias in config["use_branches"]]
    met_sites = ["site_foo.nc", "site_bar.nc"]

    assert len(branch_names) == len(science_config) == 2
    branch_name_a, branch_name_b = branch_names
    met_site_a, met_site_b = met_sites
    key_a, key_b = science_config

    tasks = [
        (branch_name_a, met_site_a, key_a),
        (branch_name_a, met_site_a, key_b),
        (branch_name_a, met_site_b, key_a),
        (branch_name_a, met_site_b, key_b),
        (branch_name_b, met_site_a, key_a),
        (branch_name_b, met_site_a, key_b),
        (branch_name_b, met_site_b, key_a),
        (branch_name_b, met_site_b, key_b),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=tmp_path)

    assert len(list(tmp_path.glob("*"))) == 2
    assert Path(tmp_path, "src").exists()
    assert Path(tmp_path, "runs").exists()
    assert Path(tmp_path, "runs", "site").exists()
    assert Path(tmp_path, "runs", "site", "logs").exists()
    # TODO(Sean) remove runs/site/namelists requirement
    assert Path(tmp_path, "runs", "site", "namelists").exists()
    assert Path(tmp_path, "runs", "site", "outputs").exists()
    assert Path(tmp_path, "runs", "site", "restart_files").exists()
    assert Path(tmp_path, "runs", "site", "tasks").exists()

    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_a}_site_foo_{key_a}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_a}_site_foo_{key_b}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_a}_site_bar_{key_a}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_a}_site_bar_{key_b}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_b}_site_foo_{key_a}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_b}_site_foo_{key_b}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_b}_site_bar_{key_a}").exists()
    assert Path(tmp_path, "runs", "site", "tasks", f"{branch_name_b}_site_bar_{key_b}").exists()


def test_clean_directory_tree(tmp_path):
    """Tests for `clean_directory_tree()`."""

    # Success case: directory tree does not exist after clean
    config = make_barebones_config()
    science_config = make_barbones_science_config()
    branch_names = [config[branch_alias]["name"] for branch_alias in config["use_branches"]]
    met_sites = ["site_foo", "site_bar"]

    assert len(branch_names) == len(science_config) == 2
    branch_name_a, branch_name_b = branch_names
    met_site_a, met_site_b = met_sites
    key_a, key_b = science_config

    tasks = [
        (branch_name_a, met_site_a, key_a),
        (branch_name_a, met_site_a, key_b),
        (branch_name_a, met_site_b, key_a),
        (branch_name_a, met_site_b, key_b),
        (branch_name_b, met_site_a, key_a),
        (branch_name_b, met_site_a, key_b),
        (branch_name_b, met_site_b, key_a),
        (branch_name_b, met_site_b, key_b),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=tmp_path)
    clean_directory_tree(root_dir=tmp_path)
    assert not Path(tmp_path, "src").exists()
    assert not Path(tmp_path, "runs").exists()
