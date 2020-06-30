from icepyx import icesat2data as ipd


def test_OA_request():
    short_name = 'ATL06'
    date_range = ['2018-10-14','2018-10-16']
    bbox = [-121, 48, -120, 49]

    region = ipd.Icesat2Data(short_name, bbox, date_range)

    region.visualize_spatial_extent(OA_quickplot=True)
    
    assert region.OA_data.empty == False

