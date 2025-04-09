"""
test different Earthdata authentication methods
"""

import netrc
import os
import shutil

import pytest


# PURPOSE: test different authentication methods
@pytest.fixture(scope="module", autouse=True)
def setup_earthdata():
    # Before test - move .netrc file to a temporary place
    netrc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    temprc_file = f"{netrc_file}.temp"
    if os.access(netrc_file, os.F_OK):
        shutil.move(netrc_file, temprc_file)
    yield
    # After test - move .netrc file back to original path
    if os.access(temprc_file, os.F_OK):
        shutil.move(temprc_file, netrc_file)
    else:
        os.remove(netrc_file)


def test_environment(username, password):
    netrc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    assert not os.access(netrc_file, os.F_OK)
    assert earthdata_login(username, password)


def test_netrc(username, password):
    # append to netrc file and set permissions level
    args = (username, "urs.earthdata.nasa.gov", password)
    netrc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    with open(netrc_file, "a+") as f:
        f.write("machine {1} login {0} password {2}\n".format(*args))
        os.chmod(netrc_file, 0o600)
    assert earthdata_login(username, password)


def earthdata_login(uid=None, pwd=None) -> bool:
    """
    Mocks passing credentials in various ways accepted by the `auth.EarthdataAuthMixin` class

    Parameters
    ----------
    uid : string, default None
        Earthdata login user ID
    pwd : string, default None
        Earthdata login password

    Returns
    -------
    success : bool
        True if completed a successful "login", else False.
    """

    try:
        url = "urs.earthdata.nasa.gov"
        mock_uid, _, mock_pwd = netrc.netrc(netrc).authenticators(url)
    except Exception:
        mock_uid = os.environ.get("EARTHDATA_USERNAME")
        mock_pwd = os.environ.get("EARTHDATA_PASSWORD")

    return bool((uid == mock_uid) & (pwd == mock_pwd))
