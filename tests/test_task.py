"""`pytest` tests for task.py"""

import unittest.mock
import subprocess
from pathlib import Path
import io
import contextlib
import pytest
import f90nml
import netCDF4

from benchcab.task import (
    patch_namelist,
    get_fluxnet_tasks,
    get_fluxnet_comparisons,
    get_comparison_name,
    run_comparison,
    Task,
    CableError,
)
from benchcab import internal
from benchcab.benchtree import setup_fluxnet_directory_tree
from .common import MOCK_CWD, make_barebones_config


def setup_mock_task() -> Task:
    """Returns a mock `Task` instance."""
    task = Task(
        branch_id=1,
        branch_name="test-branch",
        branch_patch={"cable": {"some_branch_specific_setting": True}},
        met_forcing_file="forcing-file.nc",
        sci_conf_id=0,
        sci_config={"cable": {"some_setting": True}},
    )
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
    output_path = Path(MOCK_CWD, internal.SITE_OUTPUT_DIR, task.get_output_filename())
    output_path.touch()
    assert output_path.exists()

    log_path = Path(MOCK_CWD, internal.SITE_LOG_DIR, task.get_log_filename())
    log_path.touch()
    assert log_path.exists()


def test_get_task_name():
    """Tests for `get_task_name()`."""
    # Success case: check task name convention
    task = setup_mock_task()
    assert task.get_task_name() == "forcing-file_R1_S0"


def test_get_log_filename():
    """Tests for `get_log_filename()`."""
    # Success case: check log file name convention
    task = setup_mock_task()
    assert task.get_log_filename() == "forcing-file_R1_S0_log.txt"


def test_get_output_filename():
    """Tests for `get_output_filename()`."""
    # Success case: check output file name convention
    task = setup_mock_task()
    assert task.get_output_filename() == "forcing-file_R1_S0_out.nc"


def test_fetch_files():
    """Tests for `fetch_files()`."""

    # Success case: fetch files required to run CABLE
    task = setup_mock_task()

    setup_mock_namelists_directory()
    setup_fluxnet_directory_tree([task])
    do_mock_checkout_and_build()

    task.fetch_files()

    assert Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_NML
    ).exists()
    assert Path(
        MOCK_CWD,
        internal.SITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_VEGETATION_NML,
    ).exists()
    assert Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_SOIL_NML
    ).exists()
    assert Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_EXE
    ).exists()


def test_clean_task():
    """Tests for `clean_task()`."""

    # Success case: fetch then clean files
    task = setup_mock_task()

    setup_mock_namelists_directory()
    setup_fluxnet_directory_tree([task])
    do_mock_checkout_and_build()

    task.fetch_files()

    do_mock_run(task)

    task.clean_task()

    assert not Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_NML
    ).exists()
    assert not Path(
        MOCK_CWD,
        internal.SITE_TASKS_DIR,
        task.get_task_name(),
        internal.CABLE_VEGETATION_NML,
    ).exists()
    assert not Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_SOIL_NML
    ).exists()
    assert not Path(
        MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name(), internal.CABLE_EXE
    ).exists()
    assert not Path(
        MOCK_CWD, internal.SITE_OUTPUT_DIR, task.get_output_filename()
    ).exists()
    assert not Path(MOCK_CWD, internal.SITE_LOG_DIR, task.get_log_filename()).exists()


def test_patch_namelist():
    """Tests for `patch_namelist()`."""

    nml_path = MOCK_CWD / "test.nml"

    # Success case: patch non-existing namelist file
    assert not nml_path.exists()
    patch_namelist(nml_path, {"cable": {"file": "/path/to/file", "bar": 123}})
    assert f90nml.read(nml_path) == {
        "cable": {
            "file": "/path/to/file",
            "bar": 123,
        }
    }

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


def test_setup_task():
    """Tests for `setup_task()`."""

    task = setup_mock_task()
    task_dir = Path(MOCK_CWD, internal.SITE_TASKS_DIR, task.get_task_name())

    setup_mock_namelists_directory()
    setup_fluxnet_directory_tree([task])
    do_mock_checkout_and_build()

    # Success case: test all settings are patched into task namelist file
    task.setup_task()
    res_nml = f90nml.read(str(task_dir / internal.CABLE_NML))
    assert res_nml["cable"] == {
        "filename": {
            "met": str(internal.MET_DIR / "forcing-file.nc"),
            "out": str(
                MOCK_CWD / internal.SITE_OUTPUT_DIR / task.get_output_filename()
            ),
            "log": str(MOCK_CWD / internal.SITE_LOG_DIR / task.get_log_filename()),
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
        "  Cleaning task\n"
        f"  Copying namelist files from {MOCK_CWD}/namelists to "
        f"{MOCK_CWD / 'runs/site/tasks/forcing-file_R1_S0'}\n"
        f"  Copying CABLE executable from {MOCK_CWD}/src/test-branch/"
        f"offline/cable to {MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable\n"
        "  Adding base configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable.nml\n"
        "  Adding science configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable.nml\n"
        "  Adding branch specific configurations to CABLE namelist file "
        f"{MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable.nml\n"
    )


def test_run_cable():
    """Tests for `run_cable()`."""

    task = setup_mock_task()
    task_dir = MOCK_CWD / internal.SITE_TASKS_DIR / task.get_task_name()
    task_dir.mkdir(parents=True)
    exe_path = task_dir / internal.CABLE_EXE
    exe_path.touch()
    nml_path = task_dir / internal.CABLE_NML
    nml_path.touch()

    # Success case: run CABLE executable in subprocess
    with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
        task.run_cable()
        mock_subprocess_run.assert_called_once_with(
            f"{exe_path} {nml_path} > {task_dir / internal.CABLE_STDOUT_FILENAME} 2>&1",
            shell=True,
            check=True,
        )

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run_cable()
    assert not buf.getvalue()

    # Success case: test verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
        task.run_cable(verbose=True)
    assert buf.getvalue() == (
        f"  {MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable "
        f"{MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/cable.nml "
        f"> {MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/out.txt 2>&1\n"
    )

    # Failure case: raise CableError on subprocess non-zero exit code
    with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="cmd"
        )
        with pytest.raises(CableError):
            task.run_cable()


def test_add_provenance_info():
    """Tests for `add_provenance_info()`."""

    task = setup_mock_task()
    task_dir = MOCK_CWD / internal.SITE_TASKS_DIR / task.get_task_name()
    task_dir.mkdir(parents=True)
    site_output_dir = MOCK_CWD / internal.SITE_OUTPUT_DIR
    site_output_dir.mkdir()

    # Create mock namelist file in task directory:
    f90nml.write(
        {"cable": {"filename": {"met": "/path/to/met/file", "foo": 123}, "bar": True}},
        task_dir / internal.CABLE_NML,
    )

    # Create mock netcdf output file as if CABLE had just been run:
    nc_output_path = site_output_dir / task.get_output_filename()
    netCDF4.Dataset(nc_output_path, "w")

    def mock_svn_info_show_item(*args, **kwargs):  # pylint: disable=unused-argument
        item = args[1]
        return {"url": "/url/to/test-branch", "revision": "123"}[item]

    # Success case: add global attributes to netcdf file
    with unittest.mock.patch(
        "benchcab.get_cable.svn_info_show_item", mock_svn_info_show_item
    ):
        task.add_provenance_info()

    with netCDF4.Dataset(str(nc_output_path), "r") as nc_output:
        atts = vars(nc_output)
        assert atts["cable_branch"] == "/url/to/test-branch"
        assert atts["svn_revision_number"] == "123"
        assert atts[r"filename%met"] == "/path/to/met/file"
        assert atts[r"filename%foo"] == 123
        assert atts[r"bar"] == ".true."

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "benchcab.get_cable.svn_info_show_item", mock_svn_info_show_item
    ), contextlib.redirect_stdout(io.StringIO()) as buf:
        task.add_provenance_info()
    assert not buf.getvalue()

    # Success case: test verbose output
    with unittest.mock.patch(
        "benchcab.get_cable.svn_info_show_item", mock_svn_info_show_item
    ), contextlib.redirect_stdout(io.StringIO()) as buf:
        task.add_provenance_info(verbose=True)
    assert buf.getvalue() == (
        "  Adding attributes to output file: "
        f"{MOCK_CWD}/runs/site/outputs/forcing-file_R1_S0_out.nc\n"
    )


def test_run():
    """Tests for `run()`."""

    task = setup_mock_task()

    # Success case: run CABLE and add attributes to netcdf output file
    with unittest.mock.patch(
        "benchcab.task.Task.run_cable"
    ) as mock_run_cable, unittest.mock.patch(
        "benchcab.task.Task.add_provenance_info"
    ) as mock_add_provenance_info:
        task.run()
        mock_run_cable.assert_called_once()
        mock_add_provenance_info.assert_called_once()

    # Success case: do not add attributes to netcdf file on failure
    with unittest.mock.patch(
        "benchcab.task.Task.run_cable"
    ) as mock_run_cable, unittest.mock.patch(
        "benchcab.task.Task.add_provenance_info"
    ) as mock_add_provenance_info:
        mock_run_cable.side_effect = CableError
        task.run()
        mock_run_cable.assert_called_once()
        mock_add_provenance_info.assert_not_called()

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "benchcab.task.Task.run_cable"
    ) as mock_run_cable, unittest.mock.patch(
        "benchcab.task.Task.add_provenance_info"
    ) as mock_add_provenance_info:
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            task.run()
        mock_run_cable.assert_called_once_with(verbose=False)
        mock_add_provenance_info.assert_called_once_with(verbose=False)
        assert not buf.getvalue()

    # Success case: test verbose output
    with unittest.mock.patch(
        "benchcab.task.Task.run_cable"
    ) as mock_run_cable, unittest.mock.patch(
        "benchcab.task.Task.add_provenance_info"
    ) as mock_add_provenance_info:
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            task.run(verbose=True)
        mock_run_cable.assert_called_once_with(verbose=True)
        mock_add_provenance_info.assert_called_once_with(verbose=True)
        assert buf.getvalue() == (
            "Running task forcing-file_R1_S0... CABLE standard output saved in "
            f"{MOCK_CWD}/runs/site/tasks/forcing-file_R1_S0/out.txt\n"
        )


def test_get_fluxnet_tasks():
    """Tests for `get_fluxnet_tasks()`."""

    # Success case: get task list for two branches, two met
    # sites and two science configurations
    config = make_barebones_config()
    branch_a, branch_b = config["realisations"]
    met_site_a, met_site_b = "foo", "bar"
    sci_a, sci_b = config["science_configurations"]

    assert get_fluxnet_tasks(
        config["realisations"],
        config["science_configurations"],
        [met_site_a, met_site_b],
    ) == [
        Task(0, branch_a["name"], branch_a["patch"], met_site_a, 0, sci_a),
        Task(0, branch_a["name"], branch_a["patch"], met_site_a, 1, sci_b),
        Task(0, branch_a["name"], branch_a["patch"], met_site_b, 0, sci_a),
        Task(0, branch_a["name"], branch_a["patch"], met_site_b, 1, sci_b),
        Task(1, branch_b["name"], branch_b["patch"], met_site_a, 0, sci_a),
        Task(1, branch_b["name"], branch_b["patch"], met_site_a, 1, sci_b),
        Task(1, branch_b["name"], branch_b["patch"], met_site_b, 0, sci_a),
        Task(1, branch_b["name"], branch_b["patch"], met_site_b, 1, sci_b),
    ]


def test_get_fluxnet_comparisons():
    """Tests for `get_fluxnet_comparisons()`."""

    # Success case: comparisons for two branches with two tasks
    # met0_S0_R0 met0_S0_R1
    config = make_barebones_config()
    science_configurations = [{"foo": "bar"}]
    met_sites = ["foo.nc"]
    tasks = get_fluxnet_tasks(config["realisations"], science_configurations, met_sites)
    assert len(tasks) == 2
    comparisons = get_fluxnet_comparisons(tasks)
    assert len(comparisons) == 1
    assert all(
        (task_a.sci_conf_id, task_a.met_forcing_file)
        == (task_b.sci_conf_id, task_b.met_forcing_file)
        for task_a, task_b in comparisons
    )
    assert (comparisons[0][0].branch_id, comparisons[0][1].branch_id) == (0, 1)

    # Success case: comparisons for three branches with three tasks
    # met0_S0_R0 met0_S0_R1 met0_S0_R2
    config = make_barebones_config()
    config["realisations"] += (
        {
            "name": "new-branch",
            "revision": -1,
            "path": "path/to/new-branch",
            "patch": {},
            "build_script": "",
        },
    )
    science_configurations = [{"foo": "bar"}]
    met_sites = ["foo.nc"]
    tasks = get_fluxnet_tasks(config["realisations"], science_configurations, met_sites)
    assert len(tasks) == 3
    comparisons = get_fluxnet_comparisons(tasks)
    assert len(comparisons) == 3
    assert all(
        (task_a.sci_conf_id, task_a.met_forcing_file)
        == (task_b.sci_conf_id, task_b.met_forcing_file)
        for task_a, task_b in comparisons
    )
    assert (comparisons[0][0].branch_id, comparisons[0][1].branch_id) == (0, 1)
    assert (comparisons[1][0].branch_id, comparisons[1][1].branch_id) == (0, 2)
    assert (comparisons[2][0].branch_id, comparisons[2][1].branch_id) == (1, 2)


def test_get_comparison_name():
    """Tests for `get_comparison_name()`."""
    # Success case: check comparison name convention
    task_a = Task(0, "branch-a", {}, "foo", 0, {})
    task_b = Task(1, "branch-b", {}, "foo", 0, {})
    assert get_comparison_name(task_a, task_b) == "foo_S0_R0_R1"


def test_run_comparison():
    """Tests for `run_comparison()`."""
    bitwise_cmp_dir = MOCK_CWD / internal.SITE_BITWISE_CMP_DIR
    bitwise_cmp_dir.mkdir(parents=True)
    output_dir = MOCK_CWD / internal.SITE_OUTPUT_DIR
    task_a = Task(0, "branch-a", {}, "foo", 0, {})
    task_b = Task(1, "branch-b", {}, "foo", 0, {})

    # Success case: run comparison
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 0,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        run_comparison(task_a, task_b)
        mock_subprocess_run.assert_called_once_with(
            f"nccmp -df {output_dir / task_a.get_output_filename()} "
            f"{output_dir / task_b.get_output_filename()} 2>&1",
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )

    # Success case: test non-verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 0,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            run_comparison(task_a, task_b)
        assert buf.getvalue() == (
            f"Success: files {task_a.get_output_filename()} "
            f"{task_b.get_output_filename()} are identical\n"
        )

    # Success case: test verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 0,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            run_comparison(task_a, task_b, verbose=True)
        assert buf.getvalue() == (
            f"Comparing files {task_a.get_output_filename()} and "
            f"{task_b.get_output_filename()} bitwise...\n"
            f"  nccmp -df {output_dir / task_a.get_output_filename()} "
            f"{output_dir / task_b.get_output_filename()} 2>&1\n"
            f"Success: files {task_a.get_output_filename()} "
            f"{task_b.get_output_filename()} are identical\n"
        )

    # Failure case: run comparison with non-zero exit code
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 1,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        run_comparison(task_a, task_b)
        stdout_file = bitwise_cmp_dir / f"{get_comparison_name(task_a, task_b)}.txt"
        with open(stdout_file, "r", encoding="utf-8") as file:
            assert file.read() == "standard output from subprocess"

    # Failure case: test non-verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 1,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            run_comparison(task_a, task_b)
        stdout_file = bitwise_cmp_dir / f"{get_comparison_name(task_a, task_b)}.txt"
        assert buf.getvalue() == (
            f"Failure: files {task_a.get_output_filename()} "
            f"{task_b.get_output_filename()} differ. Results of diff "
            f"have been written to {stdout_file}\n"
        )

    # Failure case: test verbose output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{
                "returncode": 1,
                "stdout": "standard output from subprocess",
            }
        )
        mock_subprocess_run.return_value = mock_completed_process
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            run_comparison(task_a, task_b, verbose=True)
        stdout_file = bitwise_cmp_dir / f"{get_comparison_name(task_a, task_b)}.txt"
        assert buf.getvalue() == (
            f"Comparing files {task_a.get_output_filename()} and "
            f"{task_b.get_output_filename()} bitwise...\n"
            f"  nccmp -df {output_dir / task_a.get_output_filename()} "
            f"{output_dir / task_b.get_output_filename()} 2>&1\n"
            f"Failure: files {task_a.get_output_filename()} "
            f"{task_b.get_output_filename()} differ. Results of diff "
            f"have been written to {stdout_file}\n"
        )
