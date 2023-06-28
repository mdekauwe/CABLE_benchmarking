"""`pytest` tests for get_cable.py"""

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
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            branch_config = setup_mock_branch_config()
            assert checkout_cable(branch_config) == MOCK_CWD / "src" / "trunk"
            mock_run_cmd.assert_called_once_with(
                "svn checkout -r 9000 https://trac.nci.org.au/svn/cable/trunk "
                f"{MOCK_CWD}/src/trunk",
                verbose=False,
            )

        # Success case: checkout mock branch repository from SVN with verbose enabled
        # TODO(Sean): this test should be removed once we use the logging module
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            branch_config = setup_mock_branch_config()
            assert (
                checkout_cable(branch_config, verbose=True)
                == MOCK_CWD / "src" / "trunk"
            )
            mock_run_cmd.assert_called_once_with(
                "svn checkout -r 9000 https://trac.nci.org.au/svn/cable/trunk "
                f"{MOCK_CWD}/src/trunk",
                verbose=True,
            )

        # Success case: specify default revision number
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            branch_config = setup_mock_branch_config()
            branch_config["revision"] = -1
            assert checkout_cable(branch_config) == MOCK_CWD / "src" / "trunk"
            mock_run_cmd.assert_called_once_with(
                f"svn checkout https://trac.nci.org.au/svn/cable/trunk {MOCK_CWD}/src/trunk",
                verbose=False,
            )

        # Success case: test non-verbose standard output
        with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                checkout_cable(branch_config)
            assert buf.getvalue() == "Successfully checked out trunk at revision 123\n"

        # Success case: test verbose standard output
        with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                checkout_cable(branch_config, verbose=True)
            assert buf.getvalue() == "Successfully checked out trunk at revision 123\n"


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
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            mock_run_cmd.side_effect = touch_files
            checkout_cable_auxiliary()
            mock_run_cmd.assert_called_once_with(
                "svn checkout https://trac.nci.org.au/svn/cable/branches/Share/CABLE-AUX "
                f"{MOCK_CWD}/{internal.CABLE_AUX_DIR}",
                verbose=False,
            )
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        # Success case: checkout CABLE-AUX repository with verbose enabled
        # TODO(Sean): this test should be removed once we use the logging module
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            mock_run_cmd.side_effect = touch_files
            checkout_cable_auxiliary(verbose=True)
            mock_run_cmd.assert_called_once_with(
                "svn checkout https://trac.nci.org.au/svn/cable/branches/Share/CABLE-AUX "
                f"{MOCK_CWD}/{internal.CABLE_AUX_DIR}",
                verbose=True,
            )
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        # Success case: test non-verbose standard output
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            mock_run_cmd.side_effect = touch_files
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                checkout_cable_auxiliary()
            assert (
                buf.getvalue() == "Successfully checked out CABLE-AUX at revision 123\n"
            )
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        # Success case: test verbose standard output
        with unittest.mock.patch(
            "benchcab.utils.subprocess.run_cmd", autospec=True
        ) as mock_run_cmd:
            mock_run_cmd.side_effect = touch_files
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                checkout_cable_auxiliary(verbose=True)
            assert (
                buf.getvalue() == "Successfully checked out CABLE-AUX at revision 123\n"
            )
        shutil.rmtree(MOCK_CWD / internal.CABLE_AUX_DIR)

        with unittest.mock.patch("benchcab.utils.subprocess.run_cmd"):
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
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd, unittest.mock.patch(
        "subprocess.CompletedProcess", autospec=True
    ) as mock_completed_process:
        mock_completed_process.configure_mock(stdout="standard output from command")
        mock_run_cmd.return_value = mock_completed_process
        assert (
            svn_info_show_item("foo", "some-mock-item")
            == "standard output from command"
        )
        mock_run_cmd.assert_called_once_with(
            "svn info --show-item some-mock-item foo", capture_output=True
        )

    # Success case: test leading and trailing white space is removed from standard output
    with unittest.mock.patch(
        "benchcab.utils.subprocess.run_cmd", autospec=True
    ) as mock_run_cmd, unittest.mock.patch(
        "subprocess.CompletedProcess", autospec=True
    ) as mock_completed_process:
        mock_completed_process.configure_mock(
            stdout="  standard output from command\n "
        )
        mock_run_cmd.return_value = mock_completed_process
        assert (
            svn_info_show_item("foo", "some-mock-item")
            == "standard output from command"
        )
        mock_run_cmd.assert_called_once_with(
            "svn info --show-item some-mock-item foo", capture_output=True
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
