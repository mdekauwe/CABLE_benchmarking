"""`pytest` tests for workdir.py"""

import io
import contextlib
import shutil
from pathlib import Path


from tests.common import MOCK_CWD
from tests.common import get_mock_config
from benchcab.fluxsite import Task
from benchcab.repository import CableRepository
from benchcab.workdir import (
    fluxsite_directory_tree_list,
    setup_fluxsite_directory_tree,
    clean_directory_tree,
    setup_src_dir,
)


def setup_mock_tasks() -> list[Task]:
    """Return a mock list of fluxsite tasks."""

    config = get_mock_config()
    repo_a = CableRepository("trunk", repo_id=0)
    repo_b = CableRepository("path/to/my-branch", repo_id=1)
    met_forcing_file_a, met_forcing_file_b = "site_foo", "site_bar"
    (sci_id_a, sci_config_a), (sci_id_b, sci_config_b) = enumerate(
        config["science_configurations"]
    )

    tasks = [
        Task(repo_a, met_forcing_file_a, sci_id_a, sci_config_a),
        Task(repo_a, met_forcing_file_a, sci_id_b, sci_config_b),
        Task(repo_a, met_forcing_file_b, sci_id_a, sci_config_a),
        Task(repo_a, met_forcing_file_b, sci_id_b, sci_config_b),
        Task(repo_b, met_forcing_file_a, sci_id_a, sci_config_a),
        Task(repo_b, met_forcing_file_a, sci_id_b, sci_config_b),
        Task(repo_b, met_forcing_file_b, sci_id_a, sci_config_a),
        Task(repo_b, met_forcing_file_b, sci_id_b, sci_config_b),
    ]

    return tasks


def setup_mock_directory_tree_list():
    """Return the list of directories for the work directory we want benchcab to create"""

    full_directory_lists = []
    full_directory_lists.append(Path(MOCK_CWD, "runs"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite", "logs"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite", "outputs"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite", "analysis"))
    full_directory_lists.append(Path(MOCK_CWD, "runs", "fluxsite",
                                "analysis", "bitwise-comparisons"))

    task_directories = []
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_foo_R0_S0"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_foo_R0_S1"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_bar_R0_S0"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_bar_R0_S1"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_foo_R1_S0"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_foo_R1_S1"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_bar_R1_S0"))
    task_directories.append(Path(MOCK_CWD, "runs", "fluxsite", "tasks", "site_bar_R1_S1"))
    full_directory_lists.append(task_directories)

    return full_directory_lists


def test_fluxsite_directory_tree_list():
    """Tests for `fluxsite_directory_tree_list()`."""

    # Success case: generate the full lists of directories for the mock tasks
    tasks = setup_mock_tasks()
    full_directory_lists = setup_mock_directory_tree_list()

    fluxsite_paths = fluxsite_directory_tree_list(
        fluxsite_tasks=tasks, root_dir=MOCK_CWD)

    assert fluxsite_paths == full_directory_lists


def test_setup_directory_tree():
    """Tests for `setup_fluxsite_directory_tree()`."""

    mock_directory_list = [Path(MOCK_CWD, "test"), Path(MOCK_CWD, "test", "test1"), [
        Path(MOCK_CWD, "test", "task1"), Path(MOCK_CWD, "test", "task2")]]

    # Success case: generate given directory structure
    tasks = setup_mock_tasks()
    setup_fluxsite_directory_tree(mock_directory_list, root_dir=MOCK_CWD)

    assert Path(MOCK_CWD, "test").exists()
    assert Path(MOCK_CWD, "test", "test1").exists()
    assert Path(MOCK_CWD, "test", "task1").exists()
    assert Path(MOCK_CWD, "test", "task2").exists()

    shutil.rmtree(MOCK_CWD / "test")

    # Success case: test non-verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        setup_fluxsite_directory_tree(mock_directory_list, root_dir=MOCK_CWD)
    assert buf.getvalue() == (
        f"Creating test directory: {MOCK_CWD}/test\n"
        f"Creating test/test1 directory: {MOCK_CWD}/test/test1\n"
        f"Creating task directories...\n"
    )

    shutil.rmtree(MOCK_CWD / "test")

    # Success case: test verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        setup_fluxsite_directory_tree(
            mock_directory_list, verbose=True, root_dir=MOCK_CWD
        )
    assert buf.getvalue() == (
        f"Creating test directory: {MOCK_CWD}/test\n"
        f"Creating test/test1 directory: {MOCK_CWD}/test/test1\n"
        f"Creating task directories...\n"
        f"Creating test/task1: "
        f"{MOCK_CWD}/test/task1\n"
        f"Creating test/task2: "
        f"{MOCK_CWD}/test/task2\n"
    )

    shutil.rmtree(MOCK_CWD / "test")


def test_clean_directory_tree():
    """Tests for `clean_directory_tree()`."""

    # Success case: directory tree does not exist after clean
    tasks = setup_mock_tasks()
    full_directory_lists = setup_mock_directory_tree_list()

    setup_fluxsite_directory_tree(full_directory_lists, root_dir=MOCK_CWD)

    clean_directory_tree(root_dir=MOCK_CWD)
    assert not Path(MOCK_CWD, "runs").exists()

    setup_src_dir(root_dir=MOCK_CWD)
    clean_directory_tree(root_dir=MOCK_CWD)
    assert not Path(MOCK_CWD, "src").exists()


def test_setup_src_dir():
    """Tests for `setup_src_dir()`."""

    # Success case: make src directory
    setup_src_dir(root_dir=MOCK_CWD)
    assert Path(MOCK_CWD, "src").exists()
