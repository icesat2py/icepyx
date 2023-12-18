import json
import os
import pytest

import icepyx as ipx
import icepyx.core.is2ref as is2ref


# Misc notes and needed tests
# test avail data and subsetting success for each input type
# (kml, shp, list of coords, bbox)
# check that downloaded data is subset?
# or is this an NSIDC level test so long as we verify the right info is submitted?


@pytest.fixture(scope="module")
def reg():
    live_reg = ipx.Query(
        "ATL06", [-55, 68, -48, 71], ["2019-02-22", "2019-02-28"], version="006"
    )
    yield live_reg
    del live_reg


@pytest.fixture(scope="module")
def session(reg):
    os.environ = {"EARTHDATA_USERNAME": "icepyx_devteam"}
    ed_obj = reg.session
    yield ed_obj
    ed_obj.close()


########## is2ref module ##########


def test_get_custom_options_output(session):
    obs = is2ref._get_custom_options(session, "ATL06", "005")
    with open("./icepyx/tests/ATL06v05_options.json") as exp_json:
        exp = json.load(exp_json)
        assert all(keys in obs.keys() for keys in exp.keys())
        assert all(obs[key] == exp[key] for key in exp.keys())


########## query module ##########
# NOTE: best this test can do at the moment is a successful download with no errors...
def test_download_granules_with_subsetting(reg, session):
    path = "./downloads_subset"
    reg.order_granules()
    reg.download_granules(path)


# def test_download_granules_without_subsetting(reg_a, session):
#     path = './downloads'
#     reg_a.order_granules(session, subset=False)
#     reg_a.download_granules(session, path)
#     #check that the max extent of the downloaded granules isn't subsetted
