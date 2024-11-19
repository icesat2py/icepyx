"""Tests for the harmony/earthaccess-enabled `QueryV2` class"""

import datetime as dt

import icepyx as ipx
from icepyx.core.queryv2 import QueryV2


def test_subset_bounding_box(tmp_path):
    """Test simple harmony subset order with bounding box and date range."""
    q = QueryV2(
        product="ATL06",
        version="006",
        spatial_extent=[-49.149, 69.186, -48.949, 69.238],
        date_range={
            "start_date": dt.datetime(2024, 4, 1, 0, 0, 0),
            "end_date": dt.datetime(2024, 4, 3, 0, 0, 0),
        },
    )

    q.download_granules(tmp_path)

    # Query should result in download of one subsetted granule.
    assert len(list(tmp_path.glob("*.h5"))) == 1

    # Ensure that the result is readable by the `Read` class
    reader = ipx.Read(tmp_path)
    reader.vars.append(
        beam_list=["gt1l", "gt3r"], var_list=["h_li", "latitude", "longitude"]
    )

    ds = reader.load()
    assert "h_li" in ds
