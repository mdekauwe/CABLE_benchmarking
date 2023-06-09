"""`pytest` tests for benchtree.py"""

import io
import contextlib
import shutil
from pathlib import Path


from tests.common import MOCK_CWD
from tests.common import make_barebones_config
from benchcab.task import Task
from benchcab.benchtree import (
    setup_fluxnet_directory_tree,
    clean_directory_tree,
    setup_src_dir,
)


def setup_mock_tasks() -> list[Task]:
    """Return a mock list of fluxnet tasks."""

    config = make_barebones_config()
    (branch_id_a, branch_a), (branch_id_b, branch_b) = enumerate(config["realisations"])
    met_site_a, met_site_b = "site_foo", "site_bar"
    (sci_id_a, sci_config_a), (sci_id_b, sci_config_b) = enumerate(
        config["science_configurations"]
    )

    tasks = [
        Task(branch_id_a, branch_a["name"], {}, met_site_a, sci_id_a, sci_config_a),
        Task(branch_id_a, branch_a["name"], {}, met_site_a, sci_id_b, sci_config_b),
        Task(branch_id_a, branch_a["name"], {}, met_site_b, sci_id_a, sci_config_a),
        Task(branch_id_a, branch_a["name"], {}, met_site_b, sci_id_b, sci_config_b),
        Task(branch_id_b, branch_b["name"], {}, met_site_a, sci_id_a, sci_config_a),
        Task(branch_id_b, branch_b["name"], {}, met_site_a, sci_id_b, sci_config_b),
        Task(branch_id_b, branch_b["name"], {}, met_site_b, sci_id_a, sci_config_a),
        Task(branch_id_b, branch_b["name"], {}, met_site_b, sci_id_b, sci_config_b),
    ]

    return tasks


def test_setup_directory_tree():
    """Tests for `setup_fluxnet_directory_tree()`."""

    # Success case: generate fluxnet directory structure
    tasks = setup_mock_tasks()
    setup_fluxnet_directory_tree(fluxnet_tasks=tasks)

    assert len(list(MOCK_CWD.glob("*"))) == 1
    assert Path(MOCK_CWD, "runs").exists()
    assert Path(MOCK_CWD, "runs", "site").exists()
    assert Path(MOCK_CWD, "runs", "site", "logs").exists()
    assert Path(MOCK_CWD, "runs", "site", "outputs").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks").exists()
    assert Path(MOCK_CWD, "runs", "site", "analysis", "bitwise-comparisons").exists()

    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_foo_R0_S0").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_foo_R0_S1").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_bar_R0_S0").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_bar_R0_S1").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_foo_R1_S0").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_foo_R1_S1").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_bar_R1_S0").exists()
    assert Path(MOCK_CWD, "runs", "site", "tasks", "site_bar_R1_S1").exists()

    shutil.rmtree(MOCK_CWD / "runs")

    # Success case: test non-verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        setup_fluxnet_directory_tree(fluxnet_tasks=tasks)
    assert buf.getvalue() == (
        f"Creating runs/site/logs directory: {MOCK_CWD}/runs/site/logs\n"
        f"Creating runs/site/outputs directory: {MOCK_CWD}/runs/site/outputs\n"
        f"Creating runs/site/tasks directory: {MOCK_CWD}/runs/site/tasks\n"
        f"Creating runs/site/analysis directory: {MOCK_CWD}/runs/site/analysis\n"
        f"Creating runs/site/analysis/bitwise-comparisons directory: {MOCK_CWD}"
        "/runs/site/analysis/bitwise-comparisons\n"
        f"Creating task directories...\n"
    )

    shutil.rmtree(MOCK_CWD / "runs")

    # Success case: test verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        setup_fluxnet_directory_tree(fluxnet_tasks=tasks, verbose=True)
    assert buf.getvalue() == (
        f"Creating runs/site/logs directory: {MOCK_CWD}/runs/site/logs\n"
        f"Creating runs/site/outputs directory: {MOCK_CWD}/runs/site/outputs\n"
        f"Creating runs/site/tasks directory: {MOCK_CWD}/runs/site/tasks\n"
        f"Creating runs/site/analysis directory: {MOCK_CWD}/runs/site/analysis\n"
        f"Creating runs/site/analysis/bitwise-comparisons directory: {MOCK_CWD}"
        "/runs/site/analysis/bitwise-comparisons\n"
        f"Creating task directories...\n"
        f"Creating runs/site/tasks/site_foo_R0_S0: {MOCK_CWD}/runs/site/tasks/site_foo_R0_S0\n"
        f"Creating runs/site/tasks/site_foo_R0_S1: {MOCK_CWD}/runs/site/tasks/site_foo_R0_S1\n"
        f"Creating runs/site/tasks/site_bar_R0_S0: {MOCK_CWD}/runs/site/tasks/site_bar_R0_S0\n"
        f"Creating runs/site/tasks/site_bar_R0_S1: {MOCK_CWD}/runs/site/tasks/site_bar_R0_S1\n"
        f"Creating runs/site/tasks/site_foo_R1_S0: {MOCK_CWD}/runs/site/tasks/site_foo_R1_S0\n"
        f"Creating runs/site/tasks/site_foo_R1_S1: {MOCK_CWD}/runs/site/tasks/site_foo_R1_S1\n"
        f"Creating runs/site/tasks/site_bar_R1_S0: {MOCK_CWD}/runs/site/tasks/site_bar_R1_S0\n"
        f"Creating runs/site/tasks/site_bar_R1_S1: {MOCK_CWD}/runs/site/tasks/site_bar_R1_S1\n"
    )

    shutil.rmtree(MOCK_CWD / "runs")


def test_clean_directory_tree():
    """Tests for `clean_directory_tree()`."""

    # Success case: directory tree does not exist after clean
    tasks = setup_mock_tasks()
    setup_fluxnet_directory_tree(fluxnet_tasks=tasks)

    clean_directory_tree()
    assert not Path(MOCK_CWD, "runs").exists()

    setup_src_dir()
    clean_directory_tree()
    assert not Path(MOCK_CWD, "src").exists()


def test_setup_src_dir():
    """Tests for `setup_src_dir()`."""

    # Success case: make src directory
    setup_src_dir()
    assert Path(MOCK_CWD, "src").exists()
