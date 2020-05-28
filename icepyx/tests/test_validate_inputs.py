import pytest
import warnings
import datetime as dt
import numpy as np

import icepyx.core.validate_inputs as val


########## dset_version ##########
def test_version_setting_to_latest():
    obs = val.dset_version('010',None)
    expected = '010'
    assert obs == expected

def test_neg_version_str_given():
    ermesg = "Version number must be positive"
    with pytest.raises(AssertionError, match=ermesg):
        val.dset_version('010', '-12')

def test_short_version_str_given():
    obs = val.dset_version('001', '2')
    expected = '002'
    assert obs == expected

def test_int_version():
    ermesg = "Please enter the version number as a string"
    with pytest.raises(TypeError, match=ermesg):
        val.dset_version('010', 12)

def test_old_version():
    wrng = "You are using an old version of this dataset"
    with pytest.warns(UserWarning, match=wrng):
        val.dset_version('003','001')
        

########## spatial ##########
def test_intlist_bbox():
    obs = val.spatial([-64, 66, -55, 72])
    expected = ['bounding_box', [-64, 66, -55, 72], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_floatlist_bbox():
    obs = val.spatial([-64.2, 66.2, -55.5, 72.5])
    expected = ['bounding_box', [-64.2, 66.2, -55.5, 72.5], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_list_latlon_pairs():
    out = val.spatial([[-55, 68], [-55, 71], [-48, 71], [-48, 68], [-55, 68]])
    obs = [out[0], out[1].exterior.coords.xy[0].tolist(), out[1].exterior.coords.xy[1].tolist(), out[2]]
    # expected = ['polygon', [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0], None]
    # expected = ['polygon', [[-55.0, 68.0], [-55.0, 71.0], [-48.0, 71.0], [-48.0, 68.0], [-55.0, 68.0]], None]
    expected = ['polygon', [-55.0, -55.0, -48.0, -48.0, -55.0], [68.0, 71.0, 71.0, 68.0, 68.0], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_tuple_latlon_pairs():
    out = val.spatial([(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)])
    obs = [out[0], out[1].exterior.coords.xy[0].tolist(), out[1].exterior.coords.xy[1].tolist(), out[2]]
    expected = ['polygon', [-55.0, -55.0, -48.0, -48.0, -55.0], [68.0, 71.0, 71.0, 68.0, 68.0], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_intlist_latlon_coords():
    out = val.spatial([-55, 68, -55, 71, -48, 71, -48, 68, -55, 68])
    obs = [out[0], out[1].exterior.coords.xy[0].tolist(), out[1].exterior.coords.xy[1].tolist(), out[2]]
    expected = ['polygon', [-55.0, -55.0, -48.0, -48.0, -55.0], [68.0, 71.0, 71.0, 68.0, 68.0], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_floatlist_latlon_coords():
    out = val.spatial([-55.0, 68.7, -55.0, 71, -48, 71, -48, 68.7, -55.0, 68.7])
    obs = [out[0], out[1].exterior.coords.xy[0].tolist(), out[1].exterior.coords.xy[1].tolist(), out[2]]
    expected = ['polygon', [-55.0, -55.0, -48.0, -48.0, -55.0], [68.7, 71.0, 71.0, 68.7, 68.7], None]
    for i in range(len(expected)):
        assert obs[i] == expected[i]

def test_spat_input_type():
    ermsg = 'Your spatial extent does not meet minimum input criteria'
    with pytest.raises(ValueError, match=ermsg):
        val.spatial([-64, 66, (-55, 72), 72])

def test_poly_spat_file_input():
    ermsg = "Check that the path and filename of your geometry file are correct"
    with pytest.raises(AssertionError, match=ermsg):
        val.spatial('file_path/name/invalid_type.txt')

#should there be additional tests on the valid file type if-else? If so, is this were we'd use a mock to assume
#a valid (existing) file has been passed? Otherwise we'll never get passed the assert statement...


########## temporal ##########
def test_date_range_order():
    ermsg = "Your date range is invalid"
    with pytest.raises(AssertionError, match=ermsg):
        val.temporal(['2019-03-22','2019-02-28'], None, None)

def test_bad_date_range():
    ermsg = "Your date range list is the wrong length. It should have start and end dates only."
    with pytest.raises(ValueError, match=ermsg):
        val.temporal(['2019-02-22'], None, None)

def test_time_defaults():
    obs_st, obs_end = val.temporal(['2019-02-22','2019-02-28'], None, None)
    exp_start = dt.datetime(2019,2,22,00,00,00)
    exp_end = dt.datetime(2019,2,28,23,59,59)
    assert obs_st == exp_start
    assert obs_end == exp_end

def test_time_validstr():
    obs_st, obs_end = val.temporal(['2019-02-22','2019-02-28'], '13:50:59', '23:15:00')
    exp_start = dt.datetime(2019,2,22,13,50,59)
    exp_end = dt.datetime(2019,2,28,23,15)
    assert obs_st == exp_start
    assert obs_end == exp_end

def test_starttime_validstr():
    ermsg = "Please enter your start time as a string"
    with pytest.raises(TypeError, match=ermsg):
        val.temporal(['2019-02-22','2019-02-28'], 121500, None)

def test_endtime_validstr():
    ermsg = "Please enter your end time as a string"
    with pytest.raises(TypeError, match=ermsg):
        val.temporal(['2019-02-22','2019-02-28'], '00:15:00', 235959)
