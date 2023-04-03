"""`pytest` tests for benchtree.py"""

from pathlib import Path


from tests.common import TMP_DIR
from tests.common import make_barebones_config
from benchcab.task import Task
from benchcab.benchtree import setup_fluxnet_directory_tree, clean_directory_tree, setup_src_dir
from benchcab.bench_config import get_science_config_id


def test_setup_directory_tree():
    """Tests for `setup_fluxnet_directory_tree()`."""

    # Success case: generate fluxnet directory structure
    config = make_barebones_config()
    science_config = config["science_configurations"]
    branch_id_a, branch_id_b = config["realisations"]
    branch_name_a, branch_name_b = [branch["name"] for branch in config["realisations"].values()]
    met_site_a, met_site_b = "site_foo", "site_bar"
    key_a, key_b = science_config
    sci_id_a, sci_id_b = get_science_config_id(key_a), get_science_config_id(key_b)

    tasks = [
        Task(branch_id_a, branch_name_a, {}, met_site_a, key_a, science_config[key_a]),
        Task(branch_id_a, branch_name_a, {}, met_site_a, key_b, science_config[key_b]),
        Task(branch_id_a, branch_name_a, {}, met_site_b, key_a, science_config[key_a]),
        Task(branch_id_a, branch_name_a, {}, met_site_b, key_b, science_config[key_b]),
        Task(branch_id_b, branch_name_b, {}, met_site_a, key_a, science_config[key_a]),
        Task(branch_id_b, branch_name_b, {}, met_site_a, key_b, science_config[key_b]),
        Task(branch_id_b, branch_name_b, {}, met_site_b, key_a, science_config[key_a]),
        Task(branch_id_b, branch_name_b, {}, met_site_b, key_b, science_config[key_b]),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=TMP_DIR)

    assert len(list(TMP_DIR.glob("*"))) == 1
    assert Path(TMP_DIR, "runs").exists()
    assert Path(TMP_DIR, "runs", "site").exists()
    assert Path(TMP_DIR, "runs", "site", "logs").exists()
    assert Path(TMP_DIR, "runs", "site", "outputs").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks").exists()

    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_foo_R{branch_id_a}_S{sci_id_a}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_foo_R{branch_id_a}_S{sci_id_b}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_bar_R{branch_id_a}_S{sci_id_a}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_bar_R{branch_id_a}_S{sci_id_b}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_foo_R{branch_id_b}_S{sci_id_a}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_foo_R{branch_id_b}_S{sci_id_b}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_bar_R{branch_id_b}_S{sci_id_a}").exists()
    assert Path(TMP_DIR, "runs", "site", "tasks", f"site_bar_R{branch_id_b}_S{sci_id_b}").exists()


def test_clean_directory_tree():
    """Tests for `clean_directory_tree()`."""

    # Success case: directory tree does not exist after clean
    config = make_barebones_config()
    science_config = config["science_configurations"]
    branch_id_a, branch_id_b = config["realisations"]
    branch_name_a, branch_name_b = [branch["name"] for branch in config["realisations"].values()]
    met_site_a, met_site_b = "site_foo", "site_bar"
    key_a, key_b = science_config

    tasks = [
        Task(branch_id_a, branch_name_a, {}, met_site_a, key_a, science_config[key_a]),
        Task(branch_id_a, branch_name_a, {}, met_site_a, key_b, science_config[key_b]),
        Task(branch_id_a, branch_name_a, {}, met_site_b, key_a, science_config[key_a]),
        Task(branch_id_a, branch_name_a, {}, met_site_b, key_b, science_config[key_b]),
        Task(branch_id_b, branch_name_b, {}, met_site_a, key_a, science_config[key_a]),
        Task(branch_id_b, branch_name_b, {}, met_site_a, key_b, science_config[key_b]),
        Task(branch_id_b, branch_name_b, {}, met_site_b, key_a, science_config[key_a]),
        Task(branch_id_b, branch_name_b, {}, met_site_b, key_b, science_config[key_b]),
    ]

    setup_fluxnet_directory_tree(fluxnet_tasks=tasks, root_dir=TMP_DIR)
    clean_directory_tree(root_dir=TMP_DIR)
    assert not Path(TMP_DIR, "runs").exists()

    setup_src_dir(root_dir=TMP_DIR)
    clean_directory_tree(root_dir=TMP_DIR)
    assert not Path(TMP_DIR, "src").exists()


def test_setup_src_dir():
    """Tests for `setup_src_dir()`."""

    # Success case: make src directory
    setup_src_dir(root_dir=TMP_DIR)
    assert Path(TMP_DIR, "src").exists()
