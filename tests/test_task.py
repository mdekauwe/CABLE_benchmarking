"""`pytest` tests for task.py"""

import os
from pathlib import Path
import f90nml

from benchcab.task import Task
from benchcab import internal
from benchcab.benchtree import setup_fluxnet_directory_tree

# Here we use the tmp_path fixture provided by pytest to
# run tests using a temporary directory.


def touch(path):
    """Mimics the unix `touch` command."""
    with open(path, 'a', encoding="utf-8"):
        os.utime(path, None)


def test_get_task_name():
    """Tests for `get_task_name()`."""
    # Success case: check task name convention
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})
    assert task.get_task_name() == "test-branch_forcing-file_sci_key"


def test_get_log_filename():
    """Tests for `get_log_filename()`."""
    # Success case: check log file name convention
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})
    assert task.get_log_filename() == "test-branch_forcing-file_sci_key_log.txt"


def test_get_output_filename():
    """Tests for `get_output_filename()`."""
    # Success case: check output file name convention
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})
    assert task.get_output_filename() == "test-branch_forcing-file_sci_key_out.nc"


def test_fetch_files(tmp_path):
    """Tests for `fetch_files()`."""

    # Success case: fetch files required to run CABLE
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})

    # Setup mock namelists directory in tmp_path:
    Path(tmp_path, internal.NAMELIST_DIR).mkdir()
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_NML))
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_SOIL_NML))
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_VEGETATION_NML))

    setup_fluxnet_directory_tree([task], root_dir=tmp_path)

    # Setup mock repository that has been checked out and built:
    Path(tmp_path, internal.SRC_DIR, "test-branch", "offline").mkdir(parents=True)
    touch(Path(tmp_path, internal.SRC_DIR, "test-branch", "offline", internal.CABLE_EXE))

    task.fetch_files(root_dir=tmp_path)

    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_VEGETATION_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_SOIL_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_EXE).exists()


def test_clean_task(tmp_path):
    """Tests for `clean_task()`."""

    # Success case: fetch then clean files
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})

    # Setup mock namelists directory in tmp_path:
    Path(tmp_path, internal.NAMELIST_DIR).mkdir()
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_NML))
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_SOIL_NML))
    touch(Path(tmp_path, internal.NAMELIST_DIR, internal.CABLE_VEGETATION_NML))

    setup_fluxnet_directory_tree([task], root_dir=tmp_path)

    # Setup mock repository that has been checked out and built:
    Path(tmp_path, internal.SRC_DIR, "test-branch", "offline").mkdir(parents=True)
    touch(Path(tmp_path, internal.SRC_DIR, "test-branch", "offline", internal.CABLE_EXE))

    task.fetch_files(root_dir=tmp_path)

    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_VEGETATION_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_SOIL_NML).exists()
    assert Path(tmp_path, internal.SITE_TASKS_DIR,
                task.get_task_name(), internal.CABLE_EXE).exists()

    # Make mock log files and output files as if benchcab has just been run:
    touch(Path(tmp_path, internal.SITE_OUTPUT_DIR, task.get_output_filename()))
    assert Path(tmp_path, internal.SITE_OUTPUT_DIR, task.get_output_filename()).exists()

    touch(Path(tmp_path, internal.SITE_LOG_DIR, task.get_log_filename()))
    assert Path(tmp_path, internal.SITE_LOG_DIR, task.get_log_filename()).exists()

    task.clean_task(root_dir=tmp_path)

    assert not Path(tmp_path, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_NML).exists()
    assert not Path(tmp_path, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_VEGETATION_NML).exists()
    assert not Path(tmp_path, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_SOIL_NML).exists()
    assert not Path(tmp_path, internal.SITE_TASKS_DIR,
                    task.get_task_name(), internal.CABLE_EXE).exists()
    assert not Path(tmp_path, internal.SITE_OUTPUT_DIR, task.get_output_filename()).exists()
    assert not Path(tmp_path, internal.SITE_LOG_DIR, task.get_log_filename()).exists()


def test_adjust_namelist_file(tmp_path):
    """Tests for `adjust_namelist_file()`."""

    # Success case: adjust cable namelist file
    task = Task("test-branch", "forcing-file.nc", "sci_key", {"some_setting": True})
    task_dir = Path(tmp_path, internal.SITE_TASKS_DIR, task.get_task_name())

    setup_fluxnet_directory_tree([task], root_dir=tmp_path)

    # Create mock namelist file in task directory:
    nml = {
        'cable': {
            'filename': {
                'met': "/path/to/met/file",
            },
        }
    }

    f90nml.write(nml, str(task_dir / internal.CABLE_NML))

    task.adjust_namelist_file(root_dir=tmp_path)

    res_nml = f90nml.read(str(task_dir / internal.CABLE_NML))

    output_path = Path(tmp_path, internal.SITE_OUTPUT_DIR, task.get_output_filename())
    log_path = Path(tmp_path, internal.SITE_LOG_DIR, task.get_log_filename())
    grid_file_path = Path(tmp_path, internal.GRID_FILE)
    veg_file_path = Path(tmp_path, internal.VEG_FILE)
    soil_file_path = Path(tmp_path, internal.SOIL_FILE)
    phen_file_path = Path(tmp_path, internal.PHEN_FILE)
    cnpbiome_file_path = Path(tmp_path, internal.CNPBIOME_FILE)

    assert res_nml['cable']['filename']['met'] == "forcing-file.nc"
    assert res_nml['cable']['filename']['out'] == str(output_path)
    assert res_nml['cable']['filename']['log'] == str(log_path)
    assert res_nml['cable']['filename']['restart_out'] == " "
    assert res_nml['cable']['filename']['type'] == str(grid_file_path)
    assert res_nml['cable']['filename']['veg'] == str(veg_file_path)
    assert res_nml['cable']['filename']['soil'] == str(soil_file_path)
    assert res_nml['cable']['output']['restart'] is False
    assert res_nml['cable']['fixedCO2'] == internal.CABLE_FIXED_CO2_CONC
    assert res_nml['cable']['casafile']['phen'] == str(phen_file_path)
    assert res_nml['cable']['casafile']['cnpbiome'] == str(cnpbiome_file_path)
    assert res_nml['cable']['spinup'] is False
    assert res_nml['cable']['some_setting'] is True
