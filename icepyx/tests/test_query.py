import icepyx as ipx
import pytest
import warnings

# ------------------------------------
# 		Generic Query tests
# ------------------------------------


# ------------------------------------
# 		Icepyx-specific tests
# ------------------------------------
def test_icepyx_boundingbox_query():
    reg_a = ipx.Query(
        "ATL06",
        [-64, 66, -55, 72],
        ["2019-02-22", "2019-02-28"],
        start_time="03:30:00",
        end_time="21:30:00",
        version="4",
    )
    obs_list = [
        reg_a.product,
        reg_a.dates,
        reg_a.start_time,
        reg_a.end_time,
        reg_a.product_version,
        reg_a.spatial_extent,
    ]
    exp_list = [
        "ATL06",
        ["2019-02-22", "2019-02-28"],
        "03:30:00",
        "21:30:00",
        "004",
        ["bounding box", [-64, 66, -55, 72]],
    ]

    for obs, expected in zip(obs_list, exp_list):
        assert obs == expected