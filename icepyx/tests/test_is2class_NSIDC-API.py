from icepyx import is2class as ipd
import pytest
import warnings
#from unittest.mock import patch
#import mock
#import builtins
#import getpass
import os

#test avail data and subsetting success for each input type (kml, shp, list of coords, bbox)
#check that agent key is added in event of no subsetting
#check that downloaded data is subset

@pytest.fixture
def reg_a():
    return ipd.Icesat2Data('ATL06',[-55, 68, -48, 71],['2019-02-22','2019-02-28'])

#@patch('my_module.__get_input', return_value='y')

@pytest.fixture
def session(reg_a):
    return reg_a._start_earthdata_session('icepyx_devteam', 'icepyx.dev@gmail.com', os.getenv('NSIDC_LOGIN'))


#QUESTION: should we be testing to make sure the session starts? If so, how? The below doesn't work because the 'requests.sessions.Session' isn't recognized... is this a case where I'd need to have a mock session to compare it to?
# def test_earthdata_session_started(session):
#     assert isinstance(session, 'requests.sessions.Session')

#is this something that would be better done with a mock, since it's really testing if the code is generating the right dict? If so, does it make sense to test a particular output from NSIDC?
def test_get_subsetting_options(reg_a, session):
    reg_a._get_custom_options(session)
    obs_keys = reg_a._cust_options.keys()
    exp_keys = ['options', 'fileformats', 'formatreproj', 'reprojectionONLY', 'noproj', 'variables']
    assert all(keys in obs_keys for keys in exp_keys)


#NOTE: best this test can do at the moment is a successful download with no errors... need to have more code to check the files themselves
def test_download_granules_with_subsetting(reg_a, session):
    path = './downloads_subset'
    reg_a.order_granules(session)
    reg_a.download_granules(session,path)
    
    #get filename here... not best way to test for successful download though, because also need to unzip and take files out of zipped dirs
    
#     with h5py.File(filename) as h5f:
#     #now actually check that the max extent of the downloaded granules is subsetted and that the files were downloaded
    
# #     exp = ???
# #     assert:
# #         obs == exp

        
# def test_download_granules_without_subsetting(reg_a, session):
#     path = './downloads'
#     reg_a.order_granules(session, subset=False)
#     reg_a.download_granules(session, path)
#     #check that the max extent of the downloaded granules isn't subsetted
    