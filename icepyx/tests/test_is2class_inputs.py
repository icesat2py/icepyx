from icepyx import is2class as ipd
import pytest
import warnings

def test_lowercase_dataset():
    lcds = 'atl03'
    obs = ipd._validate_dataset(lcds)
    expected = 'ATL03'
    assert obs == expected

def test_num_dataset():
    dsnum = 6
    ermsg = "Please enter a dataset string"
    with pytest.raises(TypeError, match=ermsg):
        ipd._validate_dataset(dsnum)
    
def test_bad_dataset():
    wrngds = 'atl-6'
    ermsg = "Please enter a valid dataset"
    with pytest.raises(AssertionError, match=ermsg):
        ipd._validate_dataset(wrngds)

def test_old_version():
    wrng = "You are using an old version of this dataset"
    with pytest.warns(UserWarning, match=wrng):
        ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1')
#    pytest.warns(UserWarning, ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1'), match=wrng)
# results in Icesat2Data object is not callable TypeError

def test_date_range_order():
    ermsg = "Your date range is invalid"
    with pytest.raises(AssertionError, match=ermsg):
        ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-03-22','2019-02-28'])

def test_bad_date_range():
    ermsg = "Your date range list is the wrong length. It should have start and end dates only."
    with pytest.raises(ValueError, match=ermsg):
        ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22'])


def test_time_defaults():
    reg_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
    obs_start = reg_a.start_time
    obs_end = reg_a.end_time
    exp_start = '00:00:00'
    exp_end = '23:59:59'
    assert obs_start == exp_start
    assert obs_end == exp_end

def test_spat_input_type():
    ermsg = 'Your spatial extent does not meet minimum input criteria'
    with pytest.raises(ValueError, match=ermsg):
        ipd.Icesat2Data('ATL06',[-64, 66, (-55, 72), 72],['2019-02-22','2019-02-28'])

def test_poly_spat_file_input():
    ermsg = "Check that the path and filename of your geometry file are correct"
    with pytest.raises(AssertionError, match=ermsg):
        ipd.Icesat2Data('ATL06','file_path/name/invalid_type.txt',['2019-02-22','2019-02-28'])

