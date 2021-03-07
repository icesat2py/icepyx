from icepyx.core.visualization import Visualize

def test_OA_request():
    short_name = 'ATL06'
    date_range = ['2019-4-14', '2019-4-30']
    bbox = [-58, -67, -56, -61]

    region_viz = Visualize(short_name, bbox, date_range)
    output_ds = region_viz.parallel_request_OA()

    assert output_ds.elevation.size > 0