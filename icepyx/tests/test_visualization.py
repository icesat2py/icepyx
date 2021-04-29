import pytest

from icepyx.core.visualization import Visualize


@pytest.mark.parametrize("product, date_range, bbox, expect", [
    ('ATL06',['2019-6-15', '2019-7-1'], [-64.5, -66, -63.5, -65], 3240),
    ('ATL07',['2019-7-1', '2019-8-1'], [-65, -66, -64.5, -65], 7160),
    ('ATL08',['2019-6-15', '2019-7-1'], [-18, 63, -17, 64], 852),
    ('ATL10',['2019-8-1', '2019-9-1'], [-64, -67, -60, -60], 7375),
    ('ATL12',['2019-7-1', '2019-10-1'], [-65.5, -65.5, -64.5, -65], 95),
    ('ATL13',['2019-6-1', '2019-12-1'], [-75, -51, -74, -50], 20),
])
def test_visualization_date_range(short_name, date_range, bbox, expect):

    region_viz = Visualize(short_name, bbox, date_range)
    data_size = region_viz.parallel_request_OA().size

    assert data_size == expect
    

@pytest.mark.parametrize("product, bbox, cycles, tracks, expect", [
    ('ATL06',[-64.5, -66, -63.5, -65], ['03'], ['1306'], 3240),
    ('ATL07',[-65, -66, -64.5, -65], ['04'], ['0186'], 7130),
    ('ATL08',[-18, 63, -17, 64], ['03'], ['1320'], 852),
    ('ATL10',[-64, -67, -60, -60], ['04'], ['0681'], 6015),
    ('ATL12',[-65.5, -65.5, -64.5, -65], ['05'], ['0041'], 95),
    ('ATL13',[-75, -51, -74, -50], ['05'], ['0293'], 20),
])
def test_visualization_orbits(short_name, bbox, cycles, tracks, expect):

    region_viz = Visualize(short_name, bbox, cycles=cycles, tracks=tracks)
    data_size = region_viz.parallel_request_OA().size

    assert data_size == expect
