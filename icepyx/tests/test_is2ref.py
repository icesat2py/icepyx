import pytest
import warnings

import icepyx.core.is2ref as is2ref

########## _validate_dataset ##########
def test_lowercase_dataset():
    lcds = 'atl03'
    obs = is2ref._validate_dataset(lcds)
    expected = 'ATL03'
    assert obs == expected

def test_num_dataset():
    dsnum = 6
    ermsg = "Please enter a dataset string"
    with pytest.raises(TypeError, match=ermsg):
        is2ref._validate_dataset(dsnum)
    
def test_bad_dataset():
    wrngds = 'atl-6'
    ermsg = "Please enter a valid dataset"
    with pytest.raises(AssertionError, match=ermsg):
        is2ref._validate_dataset(wrngds)


########## about_dataset ##########
#Note: requires internet connection
# def test_dataset_info():
#     obs = is2ref.about_dataset('ATL06')
#     print(obs)
#     #TestQuestion: what is a better way to do this? I think maybe use a mock, which would also deal with the dicts not matching because of the 'updated' key value
#     #That or check for the same keys and the same values where applicable
#     expected = {'feed': {'entry': [{'archive_center': 'NASA NSIDC DAAC',
#                      'associations': {'services': ['S1568899363-NSIDC_ECS',
#                                                    'S1613689509-NSIDC_ECS',
#                                                    'S1613669681-NSIDC_ECS']},
#                      'boxes': ['-90 -180 90 180'],
#                      'browse_flag': False,
#                      'coordinate_system': 'CARTESIAN',
#                      'data_center': 'NSIDC_ECS',
#                      'dataset_id': 'ATLAS/ICESat-2 L3A Land Ice Height V001',
#                      'has_formats': True,
#                      'has_spatial_subsetting': True,
#                      'has_temporal_subsetting': True,
#                      'has_transforms': False,
#                      'has_variables': True,
#                      'id': 'C1511847675-NSIDC_ECS',
#                      'links': [{'href': 'https://n5eil01u.ecs.nsidc.org/ATLAS/ATL06.001/',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://search.earthdata.nasa.gov/search/granules?p=C1511847675-NSIDC_ECS&m=-87.87967837686685!9.890967019347585!1!1!0!0%2C2&tl=1542476530!4!!&q=atl06&ok=atl06',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://openaltimetry.org/',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://doi.org/10.5067/ATLAS/ATL06.001',
#                                 'hreflang': 'en-US',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/metadata#'},
#                                {'href': 'https://doi.org/10.5067/ATLAS/ATL06.001',
#                                 'hreflang': 'en-US',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/documentation#'}],
#                      'online_access_flag': True,
#                      'orbit_parameters': {'inclination_angle': '92.0',
#                                           'number_of_orbits': '0.071428571',
#                                           'period': '94.29',
#                                           'start_circular_latitude': '0.0',
#                                           'swath_width': '36.0'},
#                      'organizations': ['NASA NSIDC DAAC',
#                                        'NASA/GSFC/EOS/ESDIS'],
#                      'original_format': 'ISO19115',
#                      'processing_level_id': 'Level 3',
#                      'short_name': 'ATL06',
#                      'summary': 'This data set (ATL06) provides geolocated, '
#                                 'land-ice surface heights (above the WGS 84 '
#                                 'ellipsoid, ITRF2014 reference frame), plus '
#                                 'ancillary parameters that can be used to '
#                                 'interpret and assess the quality of the '
#                                 'height estimates. The data were acquired by '
#                                 'the Advanced Topographic Laser Altimeter '
#                                 'System (ATLAS) instrument on board the Ice, '
#                                 'Cloud and land Elevation Satellite-2 '
#                                 '(ICESat-2) observatory.',
#                      'time_start': '2018-10-14T00:00:00.000Z',
#                      'title': 'ATLAS/ICESat-2 L3A Land Ice Height V001',
#                      'version_id': '001'},
#                     {'archive_center': 'NASA NSIDC DAAC',
#                      'associations': {'services': ['S1568899363-NSIDC_ECS',
#                                                    'S1613669681-NSIDC_ECS',
#                                                    'S1613689509-NSIDC_ECS']},
#                      'boxes': ['-90 -180 90 180'],
#                      'browse_flag': False,
#                      'coordinate_system': 'CARTESIAN',
#                      'data_center': 'NSIDC_ECS',
#                      'dataset_id': 'ATLAS/ICESat-2 L3A Land Ice Height V002',
#                      'has_formats': True,
#                      'has_spatial_subsetting': True,
#                      'has_temporal_subsetting': True,
#                      'has_transforms': False,
#                      'has_variables': True,
#                      'id': 'C1631076765-NSIDC_ECS',
#                      'links': [{'href': 'https://n5eil01u.ecs.nsidc.org/ATLAS/ATL06.002/',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://search.earthdata.nasa.gov/search/granules?p=C1631076765-NSIDC_ECS&q=atl06%20v002&m=-113.62703547966265!-24.431396484375!0!1!0!0%2C2&tl=1556125020!4',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://openaltimetry.org/',
#                                 'hreflang': 'en-US',
#                                 'length': '0.0KB',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#'},
#                                {'href': 'https://doi.org/10.5067/ATLAS/ATL06.002',
#                                 'hreflang': 'en-US',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/metadata#'},
#                                {'href': 'https://doi.org/10.5067/ATLAS/ATL06.002',
#                                 'hreflang': 'en-US',
#                                 'rel': 'http://esipfed.org/ns/fedsearch/1.1/documentation#'}],
#                      'online_access_flag': True,
#                      'orbit_parameters': {'inclination_angle': '92.0',
#                                           'number_of_orbits': '0.071428571',
#                                           'period': '94.29',
#                                           'start_circular_latitude': '0.0',
#                                           'swath_width': '36.0'},
#                      'organizations': ['NASA NSIDC DAAC',
#                                        'NASA/GSFC/EOS/ESDIS'],
#                      'original_format': 'ISO19115',
#                      'processing_level_id': 'Level 3',
#                      'short_name': 'ATL06',
#                      'summary': 'This data set (ATL06) provides geolocated, '
#                                 'land-ice surface heights (above the WGS 84 '
#                                 'ellipsoid, ITRF2014 reference frame), plus '
#                                 'ancillary parameters that can be used to '
#                                 'interpret and assess the quality of the '
#                                 'height estimates. The data were acquired by '
#                                 'the Advanced Topographic Laser Altimeter '
#                                 'System (ATLAS) instrument on board the Ice, '
#                                 'Cloud and land Elevation Satellite-2 '
#                                 '(ICESat-2) observatory.',
#                      'time_start': '2018-10-14T00:00:00.000Z',
#                      'title': 'ATLAS/ICESat-2 L3A Land Ice Height V002',
#                      'version_id': '002'}],
#           'id': 'https://cmr.earthdata.nasa.gov:443/search/collections.json?short_name=ATL06',
#           'title': 'ECHO dataset metadata',
#           'updated': '2020-04-30T17:31:19.421Z'}}
#     assert obs == expected


########## _get_custom_options ##########
#Note: requires internet connection + active NSIDC session
#Thus, the tests for this function are in the test_behind_NSIDC_API_login suite


########## _default_varlists ##########
def test_ATL09_default_varlist():
    obs = is2ref._default_varlists('ATL09')
    expected = ['delta_time','latitude','longitude', 'bsnow_h','bsnow_dens','bsnow_con','bsnow_psc','bsnow_od',
                    'cloud_flag_asr','cloud_fold_flag','cloud_flag_atm',
                    'column_od_asr','column_od_asr_qf',
                    'layer_attr','layer_bot','layer_top','layer_flag','layer_dens','layer_ib',
                    'msw_flag','prof_dist_x','prof_dist_y','apparent_surf_reflec']
    assert obs == expected