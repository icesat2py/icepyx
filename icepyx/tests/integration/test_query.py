"""
Integration tests for the Query class

See Also
--------

./test_query_spatial
"""

import glob
import os

import pytest

import icepyx as ipx
from icepyx.core.orders import DataOrder


@pytest.fixture(scope="module")
def reg():
    live_reg = ipx.Query("ATL06", [-55, 68, -48, 71], ["2019-02-22", "2019-02-28"])
    yield live_reg
    del live_reg


def test_harmony_custom_options_output(reg):
    opts = reg.show_custom_options()
    assert isinstance(opts, dict)
    assert "shortName" in opts
    assert opts["shortName"] == "ATL06"
    assert "services" in opts
    assert isinstance(opts["services"], list)
    assert opts["services"][0]["name"] == "sds/trajectory-subsetter"


########## query module ##########


@pytest.mark.downloads_data
def test_download_granules_without_subsetting(reg):
    """
    Test that granules can be ordered from NSIDC and downloaded with the `subset=False`
    option.
    """
    path = "./downloads"

    order = reg.order_granules(subset=False)
    assert isinstance(order, DataOrder)
    status = order.status()
    assert isinstance(status, dict)
    assert "status" in status

    files = reg.download_granules(path=path)
    assert isinstance(files, list)
    # check that there are the right number of files of the correct size
    h5_paths = sorted(glob.glob(pathname=f"{path}/ATL06_201902*.h5"))
    assert len(h5_paths) == 3
    assert [os.path.getsize(filename=p) for p in h5_paths] == [
        67108864,
        67108864,
        58720256,
    ]


@pytest.mark.downloads_data
def test_download_granules_without_ordering(reg):
    """
    Test that granules are automatically ordered by the download function.
    """
    path = "./downloads"

    files = reg.download_granules(path=path)
    assert isinstance(files, list)
    # check that there are the right number of files of the correct size
    h5_paths = sorted(glob.glob(pathname=f"{path}/ATL06_201902*.h5"))
    assert len(h5_paths) == 3
    assert [os.path.getsize(filename=p) for p in h5_paths] == [
        53228429,  # 50.8 MiB
        65120027,  # 62.1 MiB
        49749227,  # 47.4 MiB
    ]


def test_tracks_only():
    """
    Test that a Query can be created with only tracks specified (no cycles).
    """

    reg = ipx.Query(
        "ATL06", [151, -81, 158, -80], ["2019-12-02", "2019-12-02"], tracks=["1022"]
    )
    assert reg.tracks == ["1022"]
    assert reg.cycles == ["No orbital[cycle] parameters set"]

    assert reg.CMRparams["options[readable_granule_name][pattern]"] == "true"
    assert reg.CMRparams["readable_granule_name[]"] == [
        "ATL06_??????????????_1022????_*"
    ]

    assert reg.avail_granules(ids=True) == [["ATL06_20191202203649_10220511_007_01.h5"]]
