from icepyx import is2class as ipd
import pytest
import warnings
from unittest.mock import patch
#import mock
#import builtins
import getpass

#test avail data and subsetting success for each input type (kml, shp, list of coords, bbox)
#check that agent key is added in event of no subsetting
#check that downloaded data is subset

@pytest.fixture
def reg_a():
    return ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])

@patch("getpass.getpass")
@pytest.fixture
def session(reg_a):
    sess = reg_a.earthdata_login('icepyx_devteam', 'icepyx.dev@gmail.com')
    getpass.return_value = os.getenv('NSIDC_LOGIN')
    return sess
        
#    with mock.patch.object(builtins, 'input', lambda _: os.getenv('NSIDC_LOGIN')):

def test_download_granules_with_subsetting(reg_a, session):
    path = './downloads_subset'
    reg_a.order_granules(session)
    reg_a.download_granules(session,path)
    #now actually check that the max extent of the downloaded granules is subsetted
    
#     exp = ???
#     assert:
#         obs == exp

        
def test_download_granules_without_subsetting(reg_a, session):
    path = './downloads'
    reg_a.order_granules(session, subset=False)
    reg_a.download_granules(session, path)
    #check that the max extent of the downloaded granules isn't subsetted

#def teardown_function():
    #remove files from download directories

# def test_earthdata_login():
#     reg_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
#     obs = reg_a.earthdata_login('icepyx_devteam', 'icepyx.dev@gmail.com')
    
#     exp = ???
#     assert:
#         type(obs) == type(exp)
    
    