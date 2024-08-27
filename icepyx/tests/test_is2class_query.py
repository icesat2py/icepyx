import pytest

import icepyx as ipx

# Skip the whole module. See:
# https://docs.pytest.org/en/stable/reference/reference.html#globalvar-pytestmark
pytestmark = pytest.mark.skip("Legacy tests -- not sure if they ever passed!")


def test_CMRparams():
    reg_a = ipx.Query("ATL06", [-64, 66, -55, 72], ["2019-02-22", "2019-02-28"])
    reg_a.build_CMR_params()
    obs_keys = reg_a.CMRparams.keys()
    exp_keys_all = ["short_name", "version", "temporal"]
    exp_keys_any = ["bounding_box", "polygon"]

    assert all(keys in obs_keys for keys in exp_keys_all)
    assert any(key in obs_keys for key in exp_keys_any)


def test_reqconfig_params():
    reg_a = ipx.Query("ATL06", [-64, 66, -55, 72], ["2019-02-22", "2019-02-28"])

    # test for search params
    reg_a.build_reqconfig_params("search")
    obs_keys = reg_a.reqparams.keys()
    exp_keys_all = ["page_size"]
    assert all(keys in obs_keys for keys in exp_keys_all)

    # test for download params
    reg_a.reqparams = None
    reg_a.build_reqconfig_params("download")
    reg_a.reqparams.update({"token": "", "email": ""})
    obs_keys = reg_a.reqparams.keys()
    exp_keys_all = [
        "page_size",
        "page_num",
        "request_mode",
        "token",
        "email",
        "include_meta",
    ]
    assert all(keys in obs_keys for keys in exp_keys_all)


# BestPractices: should do additional properties tests for each potential property type (e.g. spatial extent can have type bounding_box or polygon)


# check that search results are correct (spatially, temporally, match actually available data)
