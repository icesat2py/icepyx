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
        53228429,  # 50.8 MiB
        65120027,  # 62.1 MiB
        49749227,  # 47.4 MiB
    ]
