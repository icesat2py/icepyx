from icepyx import is2class as ipd
import pytest
import warnings

#test avail data and subsetting success for each input type (kml, shp, list of coords, bbox)
#check that agent key is added in event of no subsetting
#check that downloaded data is subset

def test_earthdata_login():
    #fake test just so there's an active test in this file
    lcds = 'atl03'
    obs = ipd._validate_dataset(lcds)
    expected = 'ATL03'
    assert obs == expected