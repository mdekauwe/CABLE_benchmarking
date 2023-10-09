"""`pytest` tests for `fluxsite.py`."""

import contextlib
import io
import math
from pathlib import Path

import f90nml
import netCDF4
import pytest

from benchcab import __version__, internal
from benchcab.fluxsite import (
    CableError,
    Task,
    get_comparison_name,
    get_fluxsite_comparisons,
    get_fluxsite_tasks,
    patch_namelist,
    patch_remove_namelist,
)
from benchcab.repository import CableRepository
from benchcab.utils.subprocess import SubprocessWrapperInterface

from .common import MOCK_CWD, MockSubprocessWrapper, get_mock_config


def get_mock_task(
    subprocess_handler: SubprocessWrapperInterface = MockSubprocessWrapper(),
) -> Task:
    """Returns a mock `Task` instance."""
    repo = CableRepository(
        repo_id=1,
        path="path/to/test-branch",
        patch={"cable": {"some_branch_specific_setting": True}},
    )
    repo.subprocess_handler = subprocess_handler
    repo.root_dir = MOCK_CWD

    task = Task(
        repo=repo,
        met_forcing_file="forcing-file.nc",
        sci_conf_id=0,
        sci_config={"cable": {"some_setting": True}},
    )
    task.subprocess_handler = subprocess_handler
    task.root_dir = MOCK_CWD

    return task


def setup_mock_namelists_directory():
    """Setup a mock namelists directory in MOCK_CWD."""
    Path(MOCK_CWD, internal.NAMELIST_DIR).mkdir()

    cable_nml_path = Path(MOCK_CWD, internal.NAMELIST_DIR, internal.CABLE_NML)
    cable_nml_path.touch()
    assert cable_nml_path.exists()

    cable_soil_nml_path = Path(MOCK_CWD, internal.NAMELIST_DIR, internal.CABLE_SOIL_NML)
    cable_soil_nml_path.touch()
    assert cable_soil_nml_path.exists()

    cable_vegetation_nml_path = Path(
        MOCK_CWD, internal.NAMELIST_DIR, internal.CABLE_VEGETATION_NML
    )
    cable_vegetation_nml_path.touch()
    assert cable_vegetation_nml_path.exists()


def setup_mock_run_directory(task: Task):
    """Setup mock run directory for a single task."""
    task_dir = MOCK_CWD / internal.FLUXSITE_TASKS_DIR / task.get_task_name()
    task_dir.mkdir(parents=True)
    output_dir = MOCK_CWD / internal.FLUXSITE_OUTPUT_DIR
    output_dir.mkdir(parents=True)
    log_dir = MOCK_CWD / internal.FLUXSITE_LOG_DIR
    log_dir.mkdir(parents=True)


def do_mock_checkout_and_build():
    """Setup mock repository that has been checked out and built."""
    Path(MOCK_CWD, internal.SRC_DIR, "test-branch", "offline").mkdir(parents=True)

    cable_exe_path = Path(
        MOCK_CWD, internal.SRC_DIR, "test-branch", "offline", internal.CABLE_EXE
    )
    cable_exe_path.touch()
    assert cable_exe_path.exists()


def do_mock_run(task: Task):
    """Make mock log files and output files as if benchcab has just been run."""
    output_path = Path(
        MOCK_CWD, internal.FLUXSITE_OUTPUT_DIR, task.get_output_filename()
    )
    output_path.touch()
    assert output_path.exists()

    log_path = Path(MOCK_CWD, internal.FLUXSITE_LOG_DIR, task.get_log_filename())
    log_path.touch()
    assert log_path.exists()


def test_get_task_name():
    """Tests for `get_task_name()`."""
    # Success case: check task name convention
    task = get_mock_task()
    assert task.get_task_name() == "forcing-file_R1_S0"


def test_get_log_filename():
    """Tests for `get_log_filename()`."""
    # Success case: check log file name convention
    task = get_mock_task()
    assert task.get_log_filename() == "forcing-file_R1_S0_log.txt"


def test_get_output_filename():
    """Tests for `get_output_filename()`."""
    # Success case: check output file name convention
    task = get_mock_task()
    assert task.get_output_filename() == "forcing-file_R1_S0_out.nc"


def test_fetch_files():
    """Tests for `fetch_files()`."""
    # Success case: fetch files required to run CABLE
    task = get_mock_task()

    setup_mock_namelists_directory()
    setup_mock_run_directory(task)
    do_mock_checkout_and_build()

    task.fetch_files()

    assert Path(
        MOCK_CWD, internal.FLUXSITE_TASKS_DIR, task.get_task_name(), internal.CABLE_NML
    ).exists()
    assert Path(
        MOCK_CWD,
        internal.FLUXSITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_VEGETATION_NML,
    ).exists()
    assert Path(
        MOCK_CWD,
        internal.FLUXSITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_SOIL_NML,
    ).exists()
    assert Path(
        MOCK_CWD, internal.FLUXSITE_TASKS_DIR, task.get_task_name(), internal.CABLE_EXE
    ).exists()


def test_clean_task():
    """Tests for `clean_task()`."""
    # Success case: fetch then clean files
    task = get_mock_task()

    setup_mock_namelists_directory()
    setup_mock_run_directory(task)
    do_mock_checkout_and_build()

    task.fetch_files()

    do_mock_run(task)

    task.clean_task()

    assert not Path(
        MOCK_CWD, internal.FLUXSITE_TASKS_DIR, task.get_task_name(), internal.CABLE_NML
    ).exists()
    assert not Path(
        MOCK_CWD,
        internal.FLUXSITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_VEGETATION_NML,
    ).exists()
    assert not Path(
        MOCK_CWD,
        internal.FLUXSITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_SOIL_NML,
    ).exists()
    assert not Path(
        MOCK_CWD, internal.FLUXSITE_TASKS_DIR, task.get_task_name(), internal.CABLE_EXE
    ).exists()
    assert not Path(
        MOCK_CWD, internal.FLUXSITE_OUTPUT_DIR, task.get_output_filename()
    ).exists()
    assert not Path(
        MOCK_CWD, internal.FLUXSITE_LOG_DIR, task.get_log_filename()
    ).exists()


def test_patch_namelist():
    """Tests for `patch_namelist()`."""
    nml_path = MOCK_CWD / "test.nml"

    # Success case: patch non-existing namelist file
    assert not nml_path.exists()
    patch = {"cable": {"file": "/path/to/file", "bar": 123}}
    patch_namelist(nml_path, patch)
    assert f90nml.read(nml_path) == patch

    # Success case: patch non-empty namelist file
    patch_namelist(nml_path, {"cable": {"some": {"parameter": True}, "bar": 456}})
    assert f90nml.read(nml_path) == {
        "cable": {
            "file": "/path/to/file",
            "bar": 456,
            "some": {"parameter": True},
        }
    }

    # Success case: empty patch does nothing
    prev = f90nml.read(nml_path)
    patch_namelist(nml_path, {})
    assert f90nml.read(nml_path) == prev


def test_patch_remove_namelist():
    """Tests for `patch_remove_namelist()`."""
    nml_path = MOCK_CWD / "test.nml"

    # Success case: remove a namelist parameter from derrived type
    nml = {"cable": {"cable_user": {"some_parameter": True}}}
    f90nml.write(nml, nml_path)
    patch_remove_namelist(nml_path, nml)
    assert not f90nml.read(nml_path)["cable"]
    nml_path.unlink()

    # Success case: test existing namelist parameters are preserved
    # when removing a namelist parameter
    to_remove = {"cable": {"cable_user": {"new_feature": True}}}
    nml = {"cable": {"cable_user": {"some_parameter": True, "new_feature": True}}}
    f90nml.write(nml, nml_path)
    patch_remove_namelist(nml_path, to_remove)
    assert f90nml.read(nml_path) == {"cable": {"cable_user": {"some_parameter": True}}}
    nml_path.unlink()

    # Success case: empty patch_remove does nothing
    nml = {"cable": {"cable_user": {"some_parameter": True}}}
    f90nml.write(nml, nml_path)
    patch_remove_namelist(nml_path, {})
    assert f90nml.read(nml_path) == nml
    nml_path.unlink()

    # Failure case: patch_remove should raise KeyError when namelist parameters don't exist in
    # nml_path
    to_remove = {"cable": {"foo": {"bar": True}}}
    nml = {"cable": {"cable_user": {"some_parameter": True, "new_feature": True}}}
    f90nml.write(nml, nml_path)
    with pytest.raises(
        KeyError,
        match=f"Namelist parameters specified in `patch_remove` do not exist in {nml_path.name}.",
    ):
        patch_remove_namelist(nml_path, to_remove)
    nml_path.unlink(missing_ok=True)


def test_setup_task():
    """Tests for `setup_task()`."""
    task = get_mock_task()
    task_dir = Path(MOCK_CWD, internal.FLUXSITE_TASKS_DIR, task.get_task_name())

    setup_mock_namelists_directory()
    setup_mock_run_directory(task)
    do_mock_checkout_and_build()

    # Success case: test all settings are patched into task namelist file
    task.setup_task()
    res_nml = f90nml.read(str(task_dir / internal.CABLE_NML))
    assert res_nml["cable"] == {
        "filename": {
            "met": str(internal.MET_DIR / "forcing-file.nc"),
            "out": str(
                MOCK_CWD / internal.FLUXSITE_OUTPUT_DIR / task.get_output_filename()
            ),
            "log": str(MOCK_CWD / internal.FLUXSITE_LOG_DIR / task.get_log_filename()),
            "restart_out": " ",
            "type": str(MOCK_CWD / internal.GRID_FILE),
        },
        "output": {"restart": False},
        "fixedco2": internal.CABLE_FIXED_CO2_CONC,
        "casafile": {
            "phen": str(MOCK_CWD / internal.PHEN_FILE),
            "cnpbiome": str(MOCK_CWD / internal.CNPBIOME_FILE),
        },
        "spinup": False,
        "some_setting": True,
        "some_branch_specific_setting": True,
    }

    # Success case: test non-verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.setup_task()
    assert not buf.getvalue()

    # Success case: test verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.setup_task(verbose=True)
    assert buf.getvalue() == (
        "Setting up task: forcing-file_R1_S0\n"
        "Creating runs/fluxsite/tasks/forcing-file_R1_S0 directory\n"
        "  Cleaning task\n"
        f"  Copying namelist files from {MOCK_CWD}/namelists to "
        f"{MOCK_CWD / 'runs/fluxsite/tasks/forcing-file_R1_S0'}\n"
        f"  Copying CABLE executable from {MOCK_CWD}/src/test-branch/"
        f"offline/cable to {MOCK_CWD}/runs/fluxsite/tasks/forcing-file_R1_S0/cable\n"
        "  Adding base configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/fluxsite/tasks/forcing-file_R1_S0/cable.nml\n"
        "  Adding science configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/fluxsite/tasks/forcing-file_R1_S0/cable.nml\n"
        "  Adding branch specific configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/fluxsite/tasks/forcing-file_R1_S0/cable.nml\n"
    )


def test_run_cable():
    """Tests for `run_cable()`."""
    mock_subprocess = MockSubprocessWrapper()
    task = get_mock_task(subprocess_handler=mock_subprocess)
    task_dir = MOCK_CWD / internal.FLUXSITE_TASKS_DIR / task.get_task_name()
    task_dir.mkdir(parents=True)

    # Success case: run CABLE executable in subprocess
    task.run_cable()
    assert f"./{internal.CABLE_EXE} {internal.CABLE_NML}" in mock_subprocess.commands
    stdout_file = task_dir / internal.CABLE_STDOUT_FILENAME
    assert stdout_file.exists()

    # Success case: test non-verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run_cable()
    assert not buf.getvalue()

    # Success case: test verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run_cable(verbose=True)
    assert not buf.getvalue()

    # Failure case: raise CableError on subprocess non-zero exit code
    mock_subprocess.error_on_call = True
    with pytest.raises(CableError):
        task.run_cable()


def test_add_provenance_info():
    """Tests for `add_provenance_info()`."""
    mock_subprocess = MockSubprocessWrapper()
    task = get_mock_task(subprocess_handler=mock_subprocess)
    task_dir = MOCK_CWD / internal.FLUXSITE_TASKS_DIR / task.get_task_name()
    task_dir.mkdir(parents=True)
    fluxsite_output_dir = MOCK_CWD / internal.FLUXSITE_OUTPUT_DIR
    fluxsite_output_dir.mkdir()

    # Create mock namelist file in task directory:
    mock_namelist = {
        "cable": {"filename": {"met": "/path/to/met/file", "foo": 123}, "bar": True}
    }
    f90nml.write(mock_namelist, task_dir / internal.CABLE_NML)

    # Create mock netcdf output file as if CABLE had just been run:
    nc_output_path = fluxsite_output_dir / task.get_output_filename()
    netCDF4.Dataset(nc_output_path, "w")

    # Success case: add global attributes to netcdf file
    task.add_provenance_info()
    with netCDF4.Dataset(str(nc_output_path), "r") as nc_output:
        atts = vars(nc_output)
        assert atts["cable_branch"] == mock_subprocess.stdout
        assert atts["svn_revision_number"] == mock_subprocess.stdout
        assert atts["benchcab_version"] == __version__
        assert atts[r"filename%met"] == mock_namelist["cable"]["filename"]["met"]
        assert atts[r"filename%foo"] == mock_namelist["cable"]["filename"]["foo"]
        assert atts[r"bar"] == ".true."

    # Success case: test non-verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.add_provenance_info()
    assert not buf.getvalue()

    # Success case: test verbose output
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        task.add_provenance_info(verbose=True)
    assert buf.getvalue() == (
        "Adding attributes to output file: "
        f"{MOCK_CWD}/runs/fluxsite/outputs/forcing-file_R1_S0_out.nc\n"
    )


def test_get_fluxsite_tasks():
    """Tests for `get_fluxsite_tasks()`."""
    # Success case: get task list for two branches, two fluxsite met
    # forcing files and two science configurations
    config = get_mock_config()
    repos = [
        CableRepository(**branch_config, repo_id=id)
        for id, branch_config in enumerate(config["realisations"])
    ]
    met_forcing_file_a, met_forcing_file_b = "foo", "bar"
    sci_a, sci_b = config["science_configurations"]
    tasks = get_fluxsite_tasks(
        repos,
        config["science_configurations"],
        [met_forcing_file_a, met_forcing_file_b],
    )
    assert [(task.repo, task.met_forcing_file, task.sci_config) for task in tasks] == [
        (repos[0], met_forcing_file_a, sci_a),
        (repos[0], met_forcing_file_a, sci_b),
        (repos[0], met_forcing_file_b, sci_a),
        (repos[0], met_forcing_file_b, sci_b),
        (repos[1], met_forcing_file_a, sci_a),
        (repos[1], met_forcing_file_a, sci_b),
        (repos[1], met_forcing_file_b, sci_a),
        (repos[1], met_forcing_file_b, sci_b),
    ]


def test_get_fluxsite_comparisons():
    """Tests for `get_fluxsite_comparisons()`."""
    output_dir = MOCK_CWD / internal.FLUXSITE_OUTPUT_DIR

    # Success case: comparisons for two branches with two tasks
    # met0_S0_R0 met0_S0_R1
    task_a = Task(
        repo=CableRepository("path/to/repo_a", repo_id=0),
        met_forcing_file="foo.nc",
        sci_config={"foo": "bar"},
        sci_conf_id=0,
    )
    task_b = Task(
        repo=CableRepository("path/to/repo_b", repo_id=1),
        met_forcing_file="foo.nc",
        sci_config={"foo": "bar"},
        sci_conf_id=0,
    )
    tasks = [task_a, task_b]
    comparisons = get_fluxsite_comparisons(tasks, root_dir=MOCK_CWD)
    assert len(comparisons) == math.comb(len(tasks), 2)
    assert comparisons[0].files == (
        output_dir / task_a.get_output_filename(),
        output_dir / task_b.get_output_filename(),
    )
    assert comparisons[0].task_name == "foo_S0_R0_R1"

    # Success case: comparisons for three branches with three tasks
    # met0_S0_R0 met0_S0_R1 met0_S0_R2
    task_a = Task(
        repo=CableRepository("path/to/repo_a", repo_id=0),
        met_forcing_file="foo.nc",
        sci_config={"foo": "bar"},
        sci_conf_id=0,
    )
    task_b = Task(
        repo=CableRepository("path/to/repo_b", repo_id=1),
        met_forcing_file="foo.nc",
        sci_config={"foo": "bar"},
        sci_conf_id=0,
    )
    task_c = Task(
        repo=CableRepository("path/to/repo_b", repo_id=2),
        met_forcing_file="foo.nc",
        sci_config={"foo": "bar"},
        sci_conf_id=0,
    )
    tasks = [task_a, task_b, task_c]
    comparisons = get_fluxsite_comparisons(tasks, root_dir=MOCK_CWD)
    assert len(comparisons) == math.comb(len(tasks), 2)
    assert comparisons[0].files == (
        output_dir / task_a.get_output_filename(),
        output_dir / task_b.get_output_filename(),
    )
    assert comparisons[1].files == (
        output_dir / task_a.get_output_filename(),
        output_dir / task_c.get_output_filename(),
    )
    assert comparisons[2].files == (
        output_dir / task_b.get_output_filename(),
        output_dir / task_c.get_output_filename(),
    )
    assert comparisons[0].task_name == "foo_S0_R0_R1"
    assert comparisons[1].task_name == "foo_S0_R0_R2"
    assert comparisons[2].task_name == "foo_S0_R1_R2"


def test_get_comparison_name():
    """Tests for `get_comparison_name()`."""
    # Success case: check comparison name convention
    assert (
        get_comparison_name(
            CableRepository("path/to/repo", repo_id=0),
            CableRepository("path/to/repo", repo_id=1),
            met_forcing_file="foo.nc",
            sci_conf_id=0,
        )
        == "foo_S0_R0_R1"
    )
