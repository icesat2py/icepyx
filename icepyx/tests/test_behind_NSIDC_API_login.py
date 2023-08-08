import icepyx as ipx
import os
import pytest
import warnings


# Misc notes and needed tests
# test avail data and subsetting success for each input type (kml, shp, list of coords, bbox)
# check that downloaded data is subset? or is this an NSIDC level test so long as we verify the right info is submitted?


@pytest.fixture(
    scope="module",
    params=[
        dict(
            product="ATL14",
            spatial_extent=[20, 79, 28, 80],
            date_range=["2019-03-29", "2022-03-22"],
            version="002",
        ),
        dict(
            product="ATL06",
            spatial_extent=[-55, 68, -48, 71],
            date_range=["2019-02-22", "2019-02-28"],
            version="005",
        ),
    ],
)
def reg(request):
    return ipx.Query(**request.param)


@pytest.fixture(scope="module")
def session(reg):
    # append to netrc file and set permissions level
    args = ("icepyx_devteam", "urs.earthdata.nasa.gov", os.getenv("NSIDC_LOGIN"))
    netrc_file = os.path.join(os.path.expanduser("~"), ".netrc")
    with open(netrc_file, "a+") as f:
        f.write("machine {1} login {0} password {2}\n".format(*args))
        os.chmod(netrc_file, 0o600)

    reg.earthdata_login()
    ed_obj = reg._session
    yield ed_obj
    ed_obj.close()


########## is2ref module ##########
import icepyx.core.is2ref as is2ref
import json


def test_get_custom_options_output(session):
    obs = is2ref._get_custom_options(session, "ATL06", "005")
    with open("./icepyx/tests/ATL06v05_options.json") as exp_json:
        exp = json.load(exp_json)
        for key in exp.keys():
            assert key in obs.keys()
            assert exp[key] == obs[key]


########## query module ##########
# NOTE: best this test can do at the moment is a successful download with no errors...
def test_download_granules_with_subsetting(reg, session):
    path = "./downloads_subset"
    reg._session = session
    reg.order_granules()
    reg.download_granules(path)


# def test_download_granules_without_subsetting(reg_a, session):
#     path = './downloads'
#     reg_a.order_granules(session, subset=False)
#     reg_a.download_granules(session, path)
#     #check that the max extent of the downloaded granules isn't subsetted
