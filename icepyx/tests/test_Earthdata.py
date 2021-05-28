#!/usr/bin/env python
"""
test_Earthdata.py (05/2021)
"""
import os
import re
import netrc
import pytest
import shutil
import getpass
import warnings
import posixpath
# from icepyx.core.Earthdata import Earthdata

# PURPOSE: test different authentication methods
@pytest.fixture(scope="module", autouse=True)
def setup_earthdata():
    # Before test - move .netrc file to a temporary place
    netrc_file = os.path.join(os.path.expanduser('~'),'.netrc')
    temprc_file = f"{netrc_file}.temp"
    if os.access(netrc_file,os.F_OK):
        shutil.move(netrc_file,temprc_file)
    yield
    # After test - move .netrc file back to original path
    if os.access(temprc_file,os.F_OK):
        shutil.move(temprc_file,netrc_file)
    else:
        os.remove(netrc_file)

def capability_url(dataset,version):
    return posixpath.join("https://n5eil02u.ecs.nsidc.org","egi",
        "capabilities",f"{dataset}.{version}.xml")

def test_environment(username,password,email):
    url = capability_url("ATL06","003")
    netrc_file = os.path.join(os.path.expanduser('~'),'.netrc')
    assert not os.access(netrc_file,os.F_OK)
    assert Earthdata(username,email,url).login(attempts=1)

def test_netrc(username,password,email):
    # append to netrc file and set permissions level
    args = (username,'urs.earthdata.nasa.gov',password)
    netrc_file = os.path.join(os.path.expanduser('~'),'.netrc')
    with open(netrc_file,'a+') as f:
        f.write('machine {1} login {0} password {2}\n'.format(*args))
        os.chmod(netrc_file, 0o600)
    url = capability_url("ATL06","003")
    assert Earthdata(username,email,url).login(attempts=0)

class Earthdata:
    """
    Mocks the icepyx Earthdata login

    Parameters
    ----------
    uid : string
        Earthdata Login user name (user ID).
    email : string
        Complete email address, provided as a string.
    password : string (encrypted)
        Password for Earthdata registration associated with the uid.
    capability_url : string
        URL required to access Earthdata

    Returns
    -------
    True if completed a successful "login"
    """

    def __init__(
        self,
        uid,
        email,
        capability_url,
        pswd=os.environ.get('EARTHDATA_PASSWORD'),
    ):

        assert isinstance(uid, str), "Enter your login user id as a string"
        assert re.match(r"[^@]+@[^@]+\.[^@]+", email), \
            "Enter a properly formatted email address"

        self.netrc = None
        self.uid = uid
        self.email = email
        self.capability_url = capability_url
        self.pswd = pswd

    def _start_session(self):
        """
        Checks supplied credentials versus environmental variables
        """
        EARTHDATA_USERNAME = os.environ.get('EARTHDATA_USERNAME')
        EARTHDATA_PASSWORD = os.environ.get('EARTHDATA_PASSWORD')
        EARTHDATA_EMAIL = os.environ.get('EARTHDATA_EMAIL')
        if ((self.uid == EARTHDATA_USERNAME) &
            (self.email == EARTHDATA_EMAIL) &
            (self.pswd == EARTHDATA_PASSWORD)):
            return True
        else:
            return False

    def login(self, attempts=5):
        """
        Mocks attempting to "login" using supplied credentials
        """
        try:
            url = "urs.earthdata.nasa.gov"
            self.uid, _, self.pswd = netrc.netrc(self.netrc).authenticators(url)
            self.session = self._start_session()

        except:
            for i in range(attempts):
                try:
                    self.session = self._start_session()
                    break
                except KeyError:
                    pass
                if ((i+1) < attempts):
                    self.uid = input("Please re-enter your Earthdata user ID: ")
                    self.pswd = getpass.getpass("Earthdata Login password: ")
            else:
                raise RuntimeError("You could not successfully log in to Earthdata")

        return self.session
