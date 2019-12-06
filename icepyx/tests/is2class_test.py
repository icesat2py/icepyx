from icepyx import is2class as ipd
import pytest
import warnings

def test_lowercase_dataset():
    lcds = 'atl03'
    obs = ipd._validate_dataset(lcds)
    expected = 'ATL03'
    assert obs == expected
    
def test_old_version():
    wrng = "You are using an old version of this dataset"
    with pytest.warns(UserWarning, match=wrng):
        ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1')
#    pytest.warns(UserWarning, ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1'), match=wrng)
# results in Icesat2Data object is not callable TypeError
    

#e.g. check for valid format date input
# def test_something_raising_error():
#     msg = "Error message"
#     with pytest.raises(ValueError, match=msg):
#         region_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],[2019-02-22,'2019-02-28'], version='1')

     

    
