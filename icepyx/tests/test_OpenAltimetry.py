import icepyx as ipx
from icepyx.core.visualization import Visualize, filelist_latestcycle


def test_OA_request():
    
    short_name = 'ATL06'
    date_range = ['2019-4-14','2019-7-1']
    bbox = [2, -73, 10, -70]
    region = ipx.Query(short_name, bbox, date_range)
    filelist_nsidc = region.avail_granules(ids=True, cycles=True, tracks=True)[0]
    product = region.dataset
    cycle_list  = list(map(int, set(region.avail_granules(ids=True, cycles=True, tracks=True)[1])))
    filelist = filelist_latestcycle(filelist_nsidc, cycle_list)
    OA_viz = Visualize(filelist, bbox, product)
    oa_data = OA_viz.parallel_request_OA()
    OA_viz.visualize_elevations_holoview(oa_data)
    
    assert oa_data.empty == False



