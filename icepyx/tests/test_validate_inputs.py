import pytest
import warnings
import datetime as dt
import numpy as np

import icepyx.core.validate_inputs as val


########## prod_version ##########
def test_version_setting_to_latest():
    obs = val.prod_version("010", None)
    expected = "010"
    assert obs == expected


def test_neg_version_str_given():
    ermesg = "Version number must be positive"
    with pytest.raises(AssertionError, match=ermesg):
        val.prod_version("010", "-12")


def test_short_version_str_given():
    obs = val.prod_version("001", "2")
    expected = "002"
    assert obs == expected


def test_int_version():
    ermesg = "Please enter the version number as a string"
    with pytest.raises(TypeError, match=ermesg):
        val.prod_version("010", 12)


def test_old_version():
    wrng = "You are using an old version of this product"
    with pytest.warns(UserWarning, match=wrng):
        val.prod_version("003", "001")

########## orbital ##########


def test_cycles():
    obs = val.cycles([1, 2, 3, 4])
    exp = ["01", "02", "03", "04"]
    assert obs == exp


def test_tracks():
    obs = val.tracks([1, 2, 3, 4])
    exp = ["0001", "0002", "0003", "0004"]
    assert obs == exp


def test_cycles_negative():
    ermsg = "Cycle number must be positive"
    with pytest.raises(AssertionError, match=ermsg):
        val.cycles(-1)


def test_tracks_negative():
    ermsg = "Reference Ground Track must be positive"
    with pytest.raises(AssertionError, match=ermsg):
        val.tracks(-1)


def test_tracks_valid():
    expmsg = "Listed Reference Ground Track is not available"
    with pytest.warns(UserWarning) as record:
        val.tracks(1388)
    # check that warning message matches expected
    assert record[0].message.args[0] == expmsg
