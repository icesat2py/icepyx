#!/usr/bin/env python
u"""
test_Earthdata.py (04/2021)
"""
import os
import pytest
import shutil
import warnings
import posixpath
from icepyx.core.Earthdata import Earthdata

# PURPOSE: test different authentication methods
@pytest.fixture(scope="module", autouse=True)
def setup_earthdata():
    netrc_file = os.path.join(os.path.expanduser('~'),'.netrc')
    temprc_file = f"{netrc_file}.temp"
    if os.access(netrc_file,os.F_OK):
        shutil.move(netrc_file,temprc_file)
    yield
    # clean up
    if os.access(temprc_file,os.F_OK):
        shutil.move(temprc_file,netrc_file)
    else:
        os.remove(netrc_file)

def capability_url(dataset,version):
    return posixpath.join("https://n5eil02u.ecs.nsidc.org","egi",
        "capabilities",f"{dataset}.{version}.xml")

def test_environment(username,password,email):
    url = capability_url("ATL06","003")
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
