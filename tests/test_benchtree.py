"""`pytest` tests for benchtree.py"""

from pathlib import Path


from tests.common import make_barebones_config, make_barbones_science_config
from benchcab.task import Task
from benchcab.benchtree import setup_fluxnet_directory_tree, clean_directory_tree, setup_src_dir

# Here we use the tmp_path fixture provided by pytest to
# run tests using a temporary directory.


def test_setup_directory_tree(tmp_path):
    """Tests for `setup_fluxnet_directory_tree()`."""

    # Success case: generate fluxnet directory structure
    config = make_barebones_config()
    science_config = make_barbones_science_config()
    branch_name_a, branch_name_b = [
        config[branch_alias]["name"]
        for branch_alias in config["use_branches"]
    ]
    met_site_a, met_site_b = "site_foo", "site_bar"
    key_a, key_b = science_config

    tasks = [
        Task(branch_name_a, met_site_a, key_a, science_config[key_a]),
        Task(branch_name_a, met_site_a, key_b, science_config[key_b]),
        Task(branch_name_a, met_site_b, key_a, science_config[key_a]),
        Task(branch_name_a, met_site_b, key_b, science_config[key_b]),
        Task(branch_name_b, met_site_a, key_a, science_config[key_a]),
        Task(branch_name_b, met_site_a, key_b, science_config[key_b]),
        Task(branch_name_b, met_site_b, key_a, science_config[key_a]),
        Task(branch_name_b, met_site_b, key_b, science_config[key_b]),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=tmp_path)

    assert len(list(tmp_path.glob("*"))) == 1
    assert Path(tmp_path, "runs").exists()
    assert Path(tmp_path, "runs", "site").exists()
    assert Path(tmp_path, "runs", "site", "logs").exists()
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
    branch_name_a, branch_name_b = [
        config[branch_alias]["name"]
        for branch_alias in config["use_branches"]
    ]
    met_site_a, met_site_b = "site_foo", "site_bar"
    key_a, key_b = science_config

    tasks = [
        Task(branch_name_a, met_site_a, key_a, science_config[key_a]),
        Task(branch_name_a, met_site_a, key_b, science_config[key_b]),
        Task(branch_name_a, met_site_b, key_a, science_config[key_a]),
        Task(branch_name_a, met_site_b, key_b, science_config[key_b]),
        Task(branch_name_b, met_site_a, key_a, science_config[key_a]),
        Task(branch_name_b, met_site_a, key_b, science_config[key_b]),
        Task(branch_name_b, met_site_b, key_a, science_config[key_a]),
        Task(branch_name_b, met_site_b, key_b, science_config[key_b]),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=tmp_path)
    clean_directory_tree(root_dir=tmp_path)
    assert not Path(tmp_path, "runs").exists()

    setup_src_dir(root_dir=tmp_path)
    clean_directory_tree(root_dir=tmp_path)
    assert not Path(tmp_path, "src").exists()


def test_setup_src_dir(tmp_path):
    """Tests for `setup_src_dir()`."""

    # Success case: make src directory
    setup_src_dir(root_dir=tmp_path)
    assert Path(tmp_path, "src").exists()
