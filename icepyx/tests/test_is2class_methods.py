from icepyx import is2class as ipd
import pytest
import warnings

def test_combine_params():
    dict1 = {'key1': 0, 'key2': 1}
    dict2 = {'key3':0}
    expected = {'key1': 0, 'key2': 1, 'key3':0}
    obs = ipd.Icesat2Data.combine_params(dict1,dict2)
    assert obs == expected

#need test for static methods (_fmt_temporal or _fmt_spatial), given that these are "tested" through their submission to the data repo?

#how test for things like returning a geodataframe or figure, if at all? (see notes in is2class.py, approx lines 439 and 472)

