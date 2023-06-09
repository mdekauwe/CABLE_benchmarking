"""`pytest` tests for get_cable.py"""

import subprocess
import unittest.mock
import shutil
import io
import contextlib
import pytest

from benchcab import internal
from benchcab.get_cable import (
    checkout_cable,
    checkout_cable_auxiliary,
    svn_info_show_item,
    next_path,
)
from .common import MOCK_CWD


def setup_mock_branch_config() -> dict:
    """Returns a mock branch config."""
    return {
        "name": "trunk",
        "revision": 9000,
        "path": "trunk",
        "patch": {},
        "build_script": "",
    }


def mock_svn_info_show_item(*args, **kwargs):  # pylint: disable=unused-argument
    """Side effect function used to mock `svn_info_show_item()`"""
    item = args[1]
    return {"url": "/url/to/test-branch", "revision": "123"}[item]


def test_checkout_cable():
    """Tests for `checkout_cable()`."""

    with unittest.mock.patch(
        "benchcab.get_cable.svn_info_show_item", mock_svn_info_show_item
    ):
        # Success case: checkout mock branch repository from SVN
        with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
            branch_config = setup_mock_branch_config()
            path = checkout_cable(branch_config)
            assert path == MOCK_CWD / "src" / "trunk"
            mock_subprocess_run.assert_called_once_with(
                "svn checkout -r 9000 https://trac.nci.org.au/svn/cable/trunk "
                f"{MOCK_CWD}/src/trunk",
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        # Success case: specify default revision number
        with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
            branch_config = setup_mock_branch_config()
            branch_config["revision"] = -1
            path = checkout_cable(branch_config)
            assert path == MOCK_CWD / "src" / "trunk"
            mock_subprocess_run.assert_called_once_with(
                f"svn checkout https://trac.nci.org.au/svn/cable/trunk {MOCK_CWD}/src/trunk",
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        # Success case: test non-verbose output
        with unittest.mock.patch(
            "subprocess.run"
        ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
            checkout_cable(branch_config)
        assert buf.getvalue() == "Successfully checked out trunk at revision 123\n"

        # Success case: test verbose output
        with unittest.mock.patch(
            "subprocess.run"
        ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
            checkout_cable(branch_config, verbose=True)
            mock_subprocess_run.assert_called_once_with(
                "svn checkout https://trac.nci.org.au/svn/cable/trunk "
                f"{MOCK_CWD}/src/trunk",
                shell=True,
                check=True,
                stdout=None,
                stderr=subprocess.STDOUT,
            )
        assert buf.getvalue() == (
            f"svn checkout https://trac.nci.org.au/svn/cable/trunk {MOCK_CWD}/src/trunk\n"
            "Successfully checked out trunk at revision 123\n"
        )


def test_checkout_cable_auxiliary():
    """Tests for `checkout_cable_auxiliary()`."""

    grid_file_path = MOCK_CWD / internal.GRID_FILE
    phen_file_path = MOCK_CWD / internal.PHEN_FILE
    cnpbiome_file_path = MOCK_CWD / internal.CNPBIOME_FILE

    # Generate mock files in CABLE-AUX as a side effect
    def touch_files(*args, **kwargs):  # pylint: disable=unused-argument
        grid_file_path.parent.mkdir(parents=True, exist_ok=True)
        grid_file_path.touch()
        phen_file_path.parent.mkdir(parents=True, exist_ok=True)
        phen_file_path.touch()
        cnpbiome_file_path.parent.mkdir(parents=True, exist_ok=True)
        cnpbiome_file_path.touch()

    with unittest.mock.patch(
        "benchcab.get_cable.svn_info_show_item", mock_svn_info_show_item
    ):
        # Success case: checkout CABLE-AUX repository
        with unittest.mock.patch("subprocess.run") as mock_subprocess_run:
            mock_subprocess_run.side_effect = touch_files
            checkout_cable_auxiliary()
            mock_subprocess_run.assert_called_once_with(
                "svn checkout https://trac.nci.org.au/svn/cable/branches/Share/CABLE-AUX "
                f"{MOCK_CWD}/{internal.CABLE_AUX_DIR}",
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        # Success case: test non-verbose output
        with unittest.mock.patch(
            "subprocess.run"
        ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
            mock_subprocess_run.side_effect = touch_files
            checkout_cable_auxiliary()
        assert buf.getvalue() == "Successfully checked out CABLE-AUX at revision 123\n"
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        # Success case: test verbose output
        with unittest.mock.patch(
            "subprocess.run"
        ) as mock_subprocess_run, contextlib.redirect_stdout(io.StringIO()) as buf:
            mock_subprocess_run.side_effect = touch_files
            checkout_cable_auxiliary(verbose=True)
            mock_subprocess_run.assert_called_once_with(
                "svn checkout https://trac.nci.org.au/svn/cable/branches/Share/CABLE-AUX "
                f"{MOCK_CWD}/{internal.CABLE_AUX_DIR}",
                shell=True,
                check=True,
                stdout=None,
                stderr=subprocess.STDOUT,
            )
        assert buf.getvalue() == (
            "svn checkout https://trac.nci.org.au/svn/cable/branches/Share/CABLE-AUX "
            f"{MOCK_CWD}/{internal.CABLE_AUX_DIR}\n"
            "Successfully checked out CABLE-AUX at revision 123\n"
        )
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        with unittest.mock.patch("subprocess.run"):
            # Failure case: missing grid file in CABLE-AUX repository
            touch_files()
            grid_file_path.unlink()
            with pytest.raises(
                RuntimeError,
                match=f"Error checking out CABLE-AUX: cannot find file '{internal.GRID_FILE}'",
            ):
                checkout_cable_auxiliary()
            shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

            # Failure case: missing phen file in CABLE-AUX repository
            touch_files()
            phen_file_path.unlink()
            with pytest.raises(
                RuntimeError,
                match=f"Error checking out CABLE-AUX: cannot find file '{internal.PHEN_FILE}'",
            ):
                checkout_cable_auxiliary()
            shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

            # Failure case: missing cnpbiome file in CABLE-AUX repository
            touch_files()
            cnpbiome_file_path.unlink()
            with pytest.raises(
                RuntimeError,
                match=f"Error checking out CABLE-AUX: cannot find file '{internal.CNPBIOME_FILE}'",
            ):
                checkout_cable_auxiliary()
            shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)


def test_svn_info_show_item():
    """Tests for `svn_info_show_item()`."""

    # Success case: run command for mock item
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{"stdout": "standard output from command"}
        )
        mock_subprocess_run.return_value = mock_completed_process
        ret = svn_info_show_item("foo", "some-mock-item")
        assert ret == "standard output from command"
        mock_subprocess_run.assert_called_once_with(
            "svn info --show-item some-mock-item foo",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )

    # Success case: test leading and trailing white space is removed from standard output
    with unittest.mock.patch(
        "subprocess.run"
    ) as mock_subprocess_run, unittest.mock.patch(
        "subprocess.CompletedProcess"
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            **{"stdout": "  standard output from command\n "}
        )
        mock_subprocess_run.return_value = mock_completed_process
        ret = svn_info_show_item("foo", "some-mock-item")
        assert ret == "standard output from command"
        mock_subprocess_run.assert_called_once_with(
            "svn info --show-item some-mock-item foo",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )


def test_next_path():
    """Tests for `next_path()`."""

    pattern = "rev_number-*.log"

    # Success case: get next path in 'empty' CWD
    assert len(list(MOCK_CWD.glob(pattern))) == 0
    ret = next_path(pattern)
    assert ret == "rev_number-1.log"

    # Success case: get next path in 'non-empty' CWD
    ret_path = MOCK_CWD / ret
    ret_path.touch()
    assert len(list(MOCK_CWD.glob(pattern))) == 1
    ret = next_path(pattern)
    assert ret == "rev_number-2.log"
