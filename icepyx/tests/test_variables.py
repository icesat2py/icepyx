import json

import pytest

from icepyx.core.variables import Variables
from icepyx.core.query import Query
import icepyx.core.variables as variables


@pytest.fixture()
def variables_obj_atl06():
    return Variables(
        "file", 
        path='./test_data/processed_ATL06_20191130112041_09860505_006_01.h5',
        product='ATL06'
    )

@pytest.fixture()
def avail_vars_atl06():
    expected_path = './expected_outputs/vars_avail_processed_ATL06_20191130112041_09860505_006_01.h5.txt'
    with open(expected_path, 'r') as f:
        expected = f.read().splitlines()
    return expected

def test_list_of_dict_vals():
    testdict = {
        "sc_orient": ["orbit_info/sc_orient"],
        "data_start_utc": ["ancillary_data/data_start_utc"],
        "data_end_utc": ["ancillary_data/data_end_utc"],
        "h_li": ["gt1l/land_ice_segments/h_li"],
        "latitude": ["gt1l/land_ice_segments/latitude"],
        "longitude": ["gt1l/land_ice_segments/longitude"],
    }

    obs = variables.list_of_dict_vals(testdict)
    exp = [
        "orbit_info/sc_orient",
        "ancillary_data/data_start_utc",
        "ancillary_data/data_end_utc",
        "gt1l/land_ice_segments/h_li",
        "gt1l/land_ice_segments/latitude",
        "gt1l/land_ice_segments/longitude",
    ]

    assert obs == exp

def test_avail_from_file(variables_obj_atl06, avail_vars_atl06):
    assert variables_obj_atl06.avail() == avail_vars_atl06


def test_avail_from_order(avail_vars_atl06):
    region = Query('ATL06',[-45, 74, -44,75],['2019-11-30','2019-11-30'], \
                       start_time='00:00:00', end_time='23:59:59')
    # This login method assumes you have a .netrc with your EDL credentials
    region.earthdata_login()
   
    # The Query above should only ever return 1 granule. If this is ever not true,
    # raise an error
    if region.avail_granules()['Number of available granules'] != 1:
        raise TypeError('More or less than one matching granule found.')
        
    assert region.order_vars.avail().sort() == avail_vars_atl06.sort()
    
def test_append_default_vars(variables_obj_atl06):
    variables_obj_atl06.append(defaults=True)
    
    expected_path = './expected_outputs/vars_default_processed_ATL06_20191130112041_09860505_006_01.json'
    with open(expected_path, 'r') as f:
        expected = json.load(f)
    
    assert variables_obj_atl06.wanted == expected
    
def test_remove_wanted_vars(variables_obj_atl06):
    variables_obj_atl06.append(defaults=True)
    variables_obj_atl06.remove(all=True)
    
    assert variables_obj_atl06.wanted == None

def test_append_list_vars(variables_obj_atl06):
    expected = {
        'sc_orient': ['orbit_info/sc_orient'],
        'atlas_sdp_gps_epoch': ['ancillary_data/atlas_sdp_gps_epoch'],
        'cycle_number': ['orbit_info/cycle_number'],
        'rgt': ['orbit_info/rgt'],
        'data_start_utc': ['ancillary_data/data_start_utc'],
        'data_end_utc': ['ancillary_data/data_end_utc'],
        'latitude': ['gt1l/land_ice_segments/latitude',
                     'gt1r/land_ice_segments/latitude',
                     'gt2l/land_ice_segments/latitude',
                     'gt2r/land_ice_segments/latitude',
                     'gt3l/land_ice_segments/latitude',
                     'gt3r/land_ice_segments/latitude'],
        'longitude': ['gt1l/land_ice_segments/longitude',
                      'gt1r/land_ice_segments/longitude',
                      'gt2l/land_ice_segments/longitude',
                      'gt2r/land_ice_segments/longitude',
                      'gt3l/land_ice_segments/longitude',
                      'gt3r/land_ice_segments/longitude']
    }
    variables_obj_atl06.append(var_list=['latitude','longitude'])
    
    assert variables_obj_atl06.wanted == expected
