import pytest

from icepyx.core.visualization import Visualize

@pytest.mark.parametrize("short_name, date_range, bbox", [
    ('ATL06',['2019-6-15', '2019-7-1'], [-64.5, -66, -63.5, -65]),
    ('ATL07',['2019-7-1', '2019-8-1'], [-65, -66, -64.5, -65]),
    ('ATL08',['2019-6-15', '2019-7-1'], [-18, 63, -17, 64]),
    ('ATL10',['2019-8-1', '2019-9-1'], [-65.5, -66, -64.5, -65]),
    ('ATL12',['2019-7-1', '2019-10-1'], [-65.5, -65.5, -64.5, -65]),
    ('ATL13',['2019-6-1', '2019-8-1'], [-75, -51, -74, -50]),
])
def test_visualization(short_name, date_range, bbox):

    region_viz = Visualize(short_name, bbox, date_range)
    cyclemap, rgtmap, OA_ds = region_viz.visualize_elevation()

    assert OA_ds.elevation.size > 0
