"""`pytest` tests for task.py"""

import os
from pathlib import Path
import f90nml

from tests.common import TMP_DIR
from benchcab.task import Task
from benchcab import internal
from benchcab.benchtree import setup_fluxnet_directory_tree


def touch(path):
    """Mimics the unix `touch` command."""
    with open(path, 'a', encoding="utf-8"):
        os.utime(path, None)


def setup_mock_task() -> Task:
    """Returns a mock `Task` instance."""
    task = Task(
        branch_id=1,
        branch_name="test-branch",
        branch_patch={"cable": {"some_branch_specific_setting": True}},
        met_forcing_file="forcing-file.nc",
        sci_conf_key="sci0",
        sci_config={"cable": {"some_setting": True}}
    )
    return task


def setup_mock_namelists_directory():
    """Setup a mock namelists directory in TMP_DIR."""
    Path(TMP_DIR, internal.NAMELIST_DIR).mkdir()

    cable_nml_path = Path(TMP_DIR, internal.NAMELIST_DIR, internal.CABLE_NML)
    touch(cable_nml_path)
    assert cable_nml_path.exists()

    cable_soil_nml_path = Path(TMP_DIR, internal.NAMELIST_DIR, internal.CABLE_SOIL_NML)
    touch(cable_soil_nml_path)
    assert cable_soil_nml_path.exists()

    cable_vegetation_nml_path = Path(TMP_DIR, internal.NAMELIST_DIR, internal.CABLE_VEGETATION_NML)
    touch(cable_vegetation_nml_path)
    assert cable_vegetation_nml_path.exists()


def do_mock_checkout_and_build():
    """Setup mock repository that has been checked out and built."""
    Path(TMP_DIR, internal.SRC_DIR, "test-branch", "offline").mkdir(parents=True)

    cable_exe_path = Path(TMP_DIR, internal.SRC_DIR, "test-branch", "offline", internal.CABLE_EXE)
    touch(cable_exe_path)
    assert cable_exe_path.exists()


def do_mock_run(task: Task):
    """Make mock log files and output files as if benchcab has just been run."""
    output_path = Path(TMP_DIR, internal.SITE_OUTPUT_DIR, task.get_output_filename())
    touch(output_path)
    assert output_path.exists()

    log_path = Path(TMP_DIR, internal.SITE_LOG_DIR, task.get_log_filename())
    touch(log_path)
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
    setup_fluxnet_directory_tree([task], root_dir=TMP_DIR)
    do_mock_checkout_and_build()

    task.fetch_files(root_dir=TMP_DIR)

    assert Path(TMP_DIR, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_NML).exists()
    assert Path(TMP_DIR, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_VEGETATION_NML).exists()
    assert Path(TMP_DIR, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_SOIL_NML).exists()
    assert Path(TMP_DIR, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_EXE).exists()


def test_clean_task():
    """Tests for `clean_task()`."""

    # Success case: fetch then clean files
    task = setup_mock_task()

    setup_mock_namelists_directory()
    setup_fluxnet_directory_tree([task], root_dir=TMP_DIR)
    do_mock_checkout_and_build()

    task.fetch_files(root_dir=TMP_DIR)

    do_mock_run(task)

    task.clean_task(root_dir=TMP_DIR)

    assert not Path(TMP_DIR, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_NML).exists()
    assert not Path(TMP_DIR, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_VEGETATION_NML).exists()
    assert not Path(TMP_DIR, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_SOIL_NML).exists()
    assert not Path(TMP_DIR, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_EXE).exists()
    assert not Path(TMP_DIR, internal.SITE_OUTPUT_DIR, task.get_output_filename()).exists()
    assert not Path(TMP_DIR, internal.SITE_LOG_DIR, task.get_log_filename()).exists()


def test_adjust_namelist_file():
    """Tests for `adjust_namelist_file()`."""

    # Success case: adjust cable namelist file
    task = setup_mock_task()
    task_dir = Path(TMP_DIR, internal.SITE_TASKS_DIR, task.get_task_name())

    setup_fluxnet_directory_tree([task], root_dir=TMP_DIR)

    # Create mock namelist file in task directory:
    nml = {
        'cable': {
            'filename': {
                'met': "/path/to/met/file",
                'foo': 123
            },
            'bar': 123
        }
    }

    f90nml.write(nml, str(task_dir / internal.CABLE_NML))

    task.adjust_namelist_file(root_dir=TMP_DIR)

    res_nml = f90nml.read(str(task_dir / internal.CABLE_NML))

    met_file_path = Path(internal.MET_DIR, "forcing-file.nc")
    output_path = Path(TMP_DIR, internal.SITE_OUTPUT_DIR, task.get_output_filename())
    log_path = Path(TMP_DIR, internal.SITE_LOG_DIR, task.get_log_filename())
    grid_file_path = Path(TMP_DIR, internal.GRID_FILE)
    phen_file_path = Path(TMP_DIR, internal.PHEN_FILE)
    cnpbiome_file_path = Path(TMP_DIR, internal.CNPBIOME_FILE)

    assert res_nml['cable']['filename']['met'] == str(met_file_path)
    assert res_nml['cable']['filename']['out'] == str(output_path)
    assert res_nml['cable']['filename']['log'] == str(log_path)
    assert res_nml['cable']['filename']['restart_out'] == " "
    assert res_nml['cable']['filename']['type'] == str(grid_file_path)
    assert res_nml['cable']['output']['restart'] is False
    assert res_nml['cable']['fixedCO2'] == internal.CABLE_FIXED_CO2_CONC
    assert res_nml['cable']['casafile']['phen'] == str(phen_file_path)
    assert res_nml['cable']['casafile']['cnpbiome'] == str(cnpbiome_file_path)
    assert res_nml['cable']['spinup'] is False
    assert res_nml['cable']['some_setting'] is True

    assert res_nml['cable']['filename']['foo'] == 123, "assert existing derived types are preserved"
    assert res_nml['cable']['bar'] == 123, "assert existing top-level parameters are preserved"


def test_setup_task():
    """Tests for `setup_task()`."""

    # Success case: test branch specific settings are patched into task namelist file
    task = setup_mock_task()
    task_dir = Path(TMP_DIR, internal.SITE_TASKS_DIR, task.get_task_name())

    setup_mock_namelists_directory()
    setup_fluxnet_directory_tree([task], root_dir=TMP_DIR)
    do_mock_checkout_and_build()

    task.setup_task(root_dir=TMP_DIR)

    res_nml = f90nml.read(str(task_dir / internal.CABLE_NML))

    assert res_nml['cable']['some_branch_specific_setting'] is True
