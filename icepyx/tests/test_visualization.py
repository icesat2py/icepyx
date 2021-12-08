import pytest

from icepyx.core.visualization import Visualize
import icepyx.core.visualization as vis


@pytest.mark.parametrize(
    "n, exp",
    [
        (
            1,
            [
                "ATL06_20200702014158_01020810_004_01.h5",
                "ATL06_20200703011618_01170810_004_01.h5",
            ],
        ),
        (
            2,
            [
                "ATL06_20200612151119_11920712_004_01.h5",
                "ATL06_20200616021517_12450710_004_01.h5",
                "ATL06_20200702014158_01020810_004_01.h5",
                "ATL06_20200703011618_01170810_004_01.h5",
            ],
        ),
        (
            3,
            [
                "ATL06_20200612151119_11920712_004_01.h5",
                "ATL06_20200616021517_12450710_004_01.h5",
                "ATL06_20200702014158_01020810_004_01.h5",
                "ATL06_20200703011618_01170810_004_01.h5",
            ],
        ),
    ],
)
def test_files_in_latest_cycles(n, exp):
    files = [
        "ATL06_20190710071617_01860412_004_01.h5",
        "ATL06_20190713182016_02390410_004_01.h5",
        "ATL06_20200612151119_11920712_004_01.h5",
        "ATL06_20200616021517_12450710_004_01.h5",
        "ATL06_20200702014158_01020810_004_01.h5",
        "ATL06_20200703011618_01170810_004_01.h5",
    ]
    cycles = [8, 7, 4]
    obs = vis.files_in_latest_n_cycles(files, cycles=cycles, n=n)
    assert obs == exp


@pytest.mark.parametrize(
    "filename, expect",
    [
        ('ATL06_20190525202604_08790310_004_01.h5', [879, 3, '2019-05-25']),
        ('ATL06_20190614194425_11840310_004_01.h5', [1184, 3, '2019-06-14']),
        ('ATL07-02_20190624063616_13290301_004_01.h5', [1329, 3, '2019-06-24']),
        ('ATL07-02_20190602190916_10010301_004_01.h5', [1001, 3, '2019-06-02']),
        ('ATL10-02_20190611072656_11310301_004_01.h5', [1131, 3, '2019-06-11']),
        ('ATL10-02_20190731045538_05060401_004_01.h5', [506, 4, '2019-07-31']),
        ('ATL12_20190615023544_11890301_004_01.h5', [1189, 3, '2019-06-15']),
        ('ATL12_20190721170332_03610401_004_01.h5', [361, 4, '2019-07-21']),
    ],
)
def test_gran_paras(filename, expect):

    para_list = vis.gran_paras(filename)

    assert para_list == expect


@pytest.mark.parametrize(
    "product, date_range, bbox, expect",
    [
        ("ATL06", ["2019-6-15", "2019-7-1"], [-64.5, -66, -63.5, -65], 3240),
        ("ATL07", ["2019-7-1", "2019-8-1"], [-65, -66, -64.5, -65], 7130),
        ("ATL08", ["2019-6-15", "2019-7-1"], [-18, 63, -17, 64], 852),
        ("ATL10", ["2019-8-1", "2019-9-1"], [-64, -67, -60, -60], 7375),
        ("ATL12", ["2019-7-1", "2019-10-1"], [-65.5, -65.5, -64.5, -65], 95),
        ("ATL13", ["2019-6-1", "2019-12-1"], [-75, -51, -74, -50], 20),
    ],
)
def test_visualization_date_range(product, date_range, bbox, expect):

    region_viz = Visualize(product=product, spatial_extent=bbox, date_range=date_range)
    data_size = region_viz.parallel_request_OA().size

    assert data_size == expect


@pytest.mark.parametrize(
    "product, bbox, cycles, tracks, expect",
    [
        ("ATL06", [-64.5, -66, -63.5, -65], ["03"], ["1306"], 3240),
        ("ATL07", [-65, -66, -64.5, -65], ["04"], ["0186"], 7130),
        ("ATL08", [-18, 63, -17, 64], ["03"], ["1320"], 852),
        ("ATL10", [-64, -67, -60, -60], ["04"], ["0681"], 6015),
        ("ATL12", [-65.5, -65.5, -64.5, -65], ["05"], ["0041"], 95),
        ("ATL13", [-75, -51, -74, -50], ["05"], ["0293"], 20),
    ],
)
def test_visualization_orbits(product, bbox, cycles, tracks, expect):

    region_viz = Visualize(
        product=product, spatial_extent=bbox, cycles=cycles, tracks=tracks
    )
    data_size = region_viz.parallel_request_OA().size

    assert data_size == expect
