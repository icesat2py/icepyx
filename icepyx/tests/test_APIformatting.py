import pytest
import warnings
import datetime as dt
from shapely.geometry import Polygon

import icepyx.core.APIformatting as apifmt


# DevNote: is this a situation where you'd ideally build a test class, since you're just repeating the
# test function with different inputs? Especially for the _fmt_spaital, where there's >2 tests?

# CMR temporal and spatial formats --> what's the best way to compare formatted text? character by character comparison of strings?

########## _fmt_temporal ##########
def test_time_fmt():
    obs = apifmt._fmt_temporal(
        dt.datetime(2019, 1, 11, 12, 30, 30), dt.datetime(2020, 10, 31, 1, 15), "time"
    )
    exp = {"time": "2019-01-11T12:30:30,2020-10-31T01:15:00"}
    assert obs == exp


def test_temporal_fmt():
    obs = apifmt._fmt_temporal(
        dt.datetime(2019, 1, 11, 12, 30, 30),
        dt.datetime(2020, 10, 31, 1, 15),
        "temporal",
    )
    exp = {"temporal": "2019-01-11T12:30:30Z,2020-10-31T01:15:00Z"}
    assert obs == exp


########## _fmt_var_subset_list ##########
def test_var_subset_list_fmt():
    obs = apifmt._fmt_var_subset_list(
        {
            "atlas_sdp_gps_epoch": ["ancillary_data/atlas_sdp_gps_epoch"],
            "data_end_utc": ["ancillary_data/data_end_utc"],
            "data_start_utc": ["ancillary_data/data_start_utc"],
            "end_delta_time": ["ancillary_data/end_delta_time"],
            "granule_end_utc": ["ancillary_data/granule_end_utc"],
            "granule_start_utc": ["ancillary_data/granule_start_utc"],
            "latitude": ["profile_2/high_rate/latitude", "profile_2/low_rate/latitude"],
            "sc_orient": ["orbit_info/sc_orient"],
            "start_delta_time": ["ancillary_data/start_delta_time"],
        }
    )
    exp = "/ancillary_data/atlas_sdp_gps_epoch,/ancillary_data/data_end_utc,/ancillary_data/data_start_utc,/ancillary_data/end_delta_time,/ancillary_data/granule_end_utc,/ancillary_data/granule_start_utc,/profile_2/high_rate/latitude,/profile_2/low_rate/latitude,/orbit_info/sc_orient,/ancillary_data/start_delta_time"
    assert obs == exp


######## _fmt_readable_granules ########
def test_readable_granules():
    obs = apifmt._fmt_readable_granules("ATL06", cycles=["02"], tracks=["1387"])
    exp = ["ATL06_??????????????_138702??_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL07", cycles=["02"], tracks=["1387"])
    exp = ["ATL07-??_??????????????_138702??_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL06", tracks=["1387"])
    exp = ["ATL06_??????????????_1387????_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL07", tracks=["1387"])
    exp = ["ATL07-??_??????????????_1387????_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL11", tracks=["1387"])
    exp = ["ATL11_1387??_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL06", cycles=["02"])
    exp = ["ATL06_??????????????_????02??_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules("ATL07", cycles=["02"])
    exp = ["ATL07-??_??????????????_????02??_*"]
    assert obs == exp
    obs = apifmt._fmt_readable_granules(
        "ATL06", files=["ATL06_20190329071316_13870211_003_*"]
    )
    exp = ["ATL06_20190329071316_13870211_003_*"]
    assert obs == exp


########## combine_params ##########
def test_combine_params():
    dict1 = {"key1": 0, "key2": 1}
    dict2 = {"key3": 10}
    obs = apifmt.combine_params(dict1, dict2)
    expected = {"key1": 0, "key2": 1, "key3": 10}
    assert obs == expected


############ to_string #############
def test_to_string():
    CMRparams = {
        "short_name": "ATL06",
        "version": "002",
        "temporal": "2019-02-20T00:00:00Z,2019-02-28T23:59:59Z",
        "bounding_box": "-55,68,-48,71",
    }
    reqparams = {"page_size": 2000, "page_num": 1}
    params = apifmt.combine_params(CMRparams, reqparams)
    obs = apifmt.to_string(params)
    expected = (
        "short_name=ATL06&version=002"
        "&temporal=2019-02-20T00:00:00Z,2019-02-28T23:59:59Z"
        "&bounding_box=-55,68,-48,71&page_size=2000&page_num=1"
    )
    assert obs == expected


########## Parameters (class) ##########


# @pytest.fixture
# def CMRparams(scope='module'):
#     return apifmt.Parameters('CMR')


def test_CMRparams_no_other_inputs():
    CMRparams = apifmt.Parameters("CMR")
    # TestQuestion: the next statement essentially tests _get_possible_keys as well, so how would I test them independently?
    assert CMRparams.poss_keys == {
        "default": ["short_name", "version"],
        "spatial": ["bounding_box", "polygon"],
        "optional": [
            "temporal",
            "options[readable_granule_name][pattern]",
            "options[spatial][or]",
            "readable_granule_name[]",
        ],
    }
    assert CMRparams.fmted_keys == {}
    assert CMRparams._check_valid_keys
    # Note: this test must be done before the next one
    if CMRparams.partype == "required":
        assert CMRparams.check_req_values() == False
    else:
        assert CMRparams.check_values() == False

    CMRparams.build_params(
        product="ATL06",
        version="003",
        start=dt.datetime(2019, 2, 20, 0, 0),
        end=dt.datetime(2019, 2, 24, 23, 59, 59),
        extent_type="bounding_box",
        spatial_extent=[-55, 68, -48, 71],
    )
    obs_fmted_params = CMRparams.fmted_keys
    exp_fmted_params = {
        "short_name": "ATL06",
        "version": "003",
        "temporal": "2019-02-20T00:00:00Z,2019-02-24T23:59:59Z",
        "bounding_box": "-55,68,-48,71",
    }
    assert obs_fmted_params == exp_fmted_params
