#!/usr/bin/env python
"""
test icepyx.core.query.Query.earthdata_login function
"""
import netrc
import os
import pytest
import shutil
import warnings

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


@pytest.mark.test_dep
def test_dep_environment(username, password):
    netrc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    assert not os.access(netrc_file, os.F_OK)
    assert earthdata_login(username, password)
    assert not earthdata_login(username, password)


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


def earthdata_login(
    uid=None, pwd=None, email=None, s3token=False, persist=False
) -> bool:
    """
    Mocks the icepyx.core.query.Query.earthdata_login function

    Parameters
        ----------
        uid : string, default None
            Earthdata login user ID
        pwd : string, default None
            Earthdata login password
        email : string, default None
            Deprecated keyword for backwards compatibility.
        s3token : boolean, default False
            Generate AWS s3 ICESat-2 data access credentials
        persist : boolean, default False
            Whether or not you would like your login credentials saved to a .netrc file.

    Returns
    -------
    success : bool
        True if completed a successful "login", else False.
    """

    try:
        url = "urs.earthdata.nasa.gov"
        mock_uid, _, mock_pwd = netrc.netrc(netrc).authenticators(url)
    except:
        pass

    if (
        os.environ.get("EDL_PASSWORD") != None
        and os.environ.get("EDL_USERNAME") != None
    ):
        mock_uid = os.environ.get("EDL_USERNAME")
        mock_pwd = os.environ.get("EDL_PASSWORD")

    elif (
        os.environ.get("EARTHDATA_PASSWORD") != None
        and os.environ.get("EARTHDATA_USERNAME") != None
    ):
        mock_uid = os.environ.get("EARTHDATA_USERNAME")
        mock_pwd = os.environ.get("EARTHDATA_PASSWORD")
        warnings.warn(
            "Please update your environment variable names to 'EDL_USERNAME' and 'EDL_PASSWORD'",
            DeprecationWarning,
        )
        # os.environ["EDL_USERNAME"] = str(uid)
        # os.environ["EDL_PASSWORD"] = str(pwd)

    # mock_uid = os.environ.get("EDL_USERNAME")
    # mock_pwd = os.environ.get("EDL_PASSWORD")

    print(uid)
    print(mock_uid)
    print(pwd)
    print(mock_pwd)

    if (uid == mock_uid) & (pwd == mock_pwd):
        return True
    else:
        return False
