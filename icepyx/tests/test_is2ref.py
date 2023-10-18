import pytest
import warnings

import icepyx.core.is2ref as is2ref

########## _validate_product ##########


def test_num_product():
    dsnum = 6
    ermsg = "A valid product string was not provided. Check user input, if given, or file metadata."
    with pytest.raises(TypeError, match=ermsg):
        is2ref._validate_product(dsnum)


def test_bad_product():
    wrngds = "atl-6"
    ermsg = "A valid product string was not provided. Check user input, if given, or file metadata."
    with pytest.raises(AssertionError, match=ermsg):
        is2ref._validate_product(wrngds)


# test all possible product types
def test_atl01_product():
    lcds = "atl01"
    obs = is2ref._validate_product(lcds)
    expected = "ATL01"
    assert obs == expected

    ucds = "ATL01"
    obs = is2ref._validate_product(ucds)
    expected = "ATL01"
    assert obs == expected


def test_atl02product():
    lcds = "atl02"
    obs = is2ref._validate_product(lcds)
    expected = "ATL02"
    assert obs == expected

    ucds = "ATL02"
    obs = is2ref._validate_product(ucds)
    expected = "ATL02"
    assert obs == expected


def test_atl03_product():
    lcds = "atl03"
    obs = is2ref._validate_product(lcds)
    expected = "ATL03"
    assert obs == expected

    ucds = "ATL03"
    obs = is2ref._validate_product(ucds)
    expected = "ATL03"
    assert obs == expected


def test_atl04_product():
    lcds = "atl04"
    obs = is2ref._validate_product(lcds)
    expected = "ATL04"
    assert obs == expected

    ucds = "ATL04"
    obs = is2ref._validate_product(ucds)
    expected = "ATL04"
    assert obs == expected


def test_atl06_product():
    lcds = "atl06"
    obs = is2ref._validate_product(lcds)
    expected = "ATL06"
    assert obs == expected

    ucds = "ATL06"
    obs = is2ref._validate_product(ucds)
    expected = "ATL06"
    assert obs == expected


def test_atl07_product():
    lcds = "atl07"
    obs = is2ref._validate_product(lcds)
    expected = "ATL07"
    assert obs == expected

    ucds = "ATL07"
    obs = is2ref._validate_product(ucds)
    expected = "ATL07"
    assert obs == expected


def test_atl07ql_product():
    lcds = "atl07ql"
    obs = is2ref._validate_product(lcds)
    expected = "ATL07QL"
    assert obs == expected

    ucds = "ATL07QL"
    obs = is2ref._validate_product(ucds)
    expected = "ATL07QL"
    assert obs == expected


def test_atl08_product():
    lcds = "atl08"
    obs = is2ref._validate_product(lcds)
    expected = "ATL08"
    assert obs == expected

    ucds = "ATL08"
    obs = is2ref._validate_product(ucds)
    expected = "ATL08"
    assert obs == expected


def test_atl09_product():
    lcds = "atl09"
    obs = is2ref._validate_product(lcds)
    expected = "ATL09"
    assert obs == expected

    ucds = "ATL09"
    obs = is2ref._validate_product(ucds)
    expected = "ATL09"
    assert obs == expected


def test_atl09ql_product():
    lcds = "atl09ql"
    obs = is2ref._validate_product(lcds)
    expected = "ATL09QL"
    assert obs == expected

    ucds = "ATL09QL"
    obs = is2ref._validate_product(ucds)
    expected = "ATL09QL"
    assert obs == expected


def test_atl10_product():
    lcds = "atl10"
    obs = is2ref._validate_product(lcds)
    expected = "ATL10"
    assert obs == expected

    ucds = "ATL10"
    obs = is2ref._validate_product(ucds)
    expected = "ATL10"
    assert obs == expected


def test_atl11_product():
    lcds = "atl11"
    obs = is2ref._validate_product(lcds)
    expected = "ATL11"
    assert obs == expected

    ucds = "ATL11"
    obs = is2ref._validate_product(ucds)
    expected = "ATL11"
    assert obs == expected


def test_atl12_product():
    lcds = "atl12"
    obs = is2ref._validate_product(lcds)
    expected = "ATL12"
    assert obs == expected

    ucds = "ATL12"
    obs = is2ref._validate_product(ucds)
    expected = "ATL12"
    assert obs == expected


def test_atl13_product():
    lcds = "atl13"
    obs = is2ref._validate_product(lcds)
    expected = "ATL13"
    assert obs == expected

    ucds = "ATL13"
    obs = is2ref._validate_product(ucds)
    expected = "ATL13"
    assert obs == expected


def test_atl14_product():
    lcds = "atl14"
    obs = is2ref._validate_product(lcds)
    expected = "ATL14"
    assert obs == expected

    ucds = "ATL14"
    obs = is2ref._validate_product(ucds)
    expected = "ATL14"
    assert obs == expected


def test_atl15_product():
    lcds = "atl15"
    obs = is2ref._validate_product(lcds)
    expected = "ATL15"
    assert obs == expected

    ucds = "ATL15"
    obs = is2ref._validate_product(ucds)
    expected = "ATL15"
    assert obs == expected


def test_atl16_product():
    lcds = "atl16"
    obs = is2ref._validate_product(lcds)
    expected = "ATL16"
    assert obs == expected

    ucds = "ATL16"
    obs = is2ref._validate_product(ucds)
    expected = "ATL16"
    assert obs == expected


def test_atl17_product():
    lcds = "atl17"
    obs = is2ref._validate_product(lcds)
    expected = "ATL17"
    assert obs == expected

    ucds = "ATL17"
    obs = is2ref._validate_product(ucds)
    expected = "ATL17"
    assert obs == expected


def test_atl19_product():
    lcds = "atl19"
    obs = is2ref._validate_product(lcds)
    expected = "ATL19"
    assert obs == expected

    ucds = "ATL19"
    obs = is2ref._validate_product(ucds)
    expected = "ATL19"
    assert obs == expected


def test_atl20_product():
    lcds = "atl20"
    obs = is2ref._validate_product(lcds)
    expected = "ATL20"
    assert obs == expected

    ucds = "ATL20"
    obs = is2ref._validate_product(ucds)
    expected = "ATL20"
    assert obs == expected


def test_atl21_product():
    lcds = "atl21"
    obs = is2ref._validate_product(lcds)
    expected = "ATL21"
    assert obs == expected

    ucds = "ATL21"
    obs = is2ref._validate_product(ucds)
    expected = "ATL21"
    assert obs == expected


def test_atl23_product():
    lcds = "atl23"
    obs = is2ref._validate_product(lcds)
    expected = "ATL23"
    assert obs == expected

    ucds = "ATL23"
    obs = is2ref._validate_product(ucds)
    expected = "ATL23"
    assert obs == expected


########## about_product ##########
# Note: requires internet connection
# could the github flat data option be used here? https://octo.github.com/projects/flat-data
# def test_product_info():
#     obs = is2ref.about_product('ATL06')
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
# Note: requires internet connection + active NSIDC session
# Thus, the tests for this function are in the test_behind_NSIDC_API_login suite


########## _default_varlists ##########


def test_ATL06_default_varlist():
    obs = is2ref._default_varlists("ATL06")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
        "h_li",
        "h_li_sigma",
        "atl06_quality_summary",
        "segment_id",
        "sigma_geo_h",
        "x_atc",
        "y_atc",
        "seg_azimuth",
        "sigma_geo_at",
        "sigma_geo_xt",
        "dh_fit_dx",
        "dh_fit_dx_sigma",
        "h_mean",
        "dh_fit_dy",
        "h_rms_misfit",
        "h_robust_sprd",
        "n_fit_photons",
        "signal_selection_source",
        "snr_significance",
        "w_surface_window_final",
        "bsnow_conf",
        "bsnow_h",
        "cloud_flg_asr",
        "cloud_flg_atm",
        "r_eff",
        "tide_ocean",
    ]
    assert obs == expected


def test_ATL07_default_varlist():
    obs = is2ref._default_varlists("ATL07")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
        "seg_dist_x",
        "height_segment_height",
        "height_segment_length_seg",
        "height_segment_ssh_flag",
        "height_segment_type",
        "height_segment_quality",
        "height_segment_confidence",
    ]
    assert obs == expected


def test_ATL09_default_varlist():
    obs = is2ref._default_varlists("ATL09")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
        "bsnow_h",
        "bsnow_dens",
        "bsnow_con",
        "bsnow_psc",
        "bsnow_od",
        "cloud_flag_asr",
        "cloud_fold_flag",
        "cloud_flag_atm",
        "column_od_asr",
        "column_od_asr_qf",
        "layer_attr",
        "layer_bot",
        "layer_top",
        "layer_flag",
        "layer_dens",
        "layer_ib",
        "msw_flag",
        "prof_dist_x",
        "prof_dist_y",
        "apparent_surf_reflec",
    ]
    assert obs == expected


def test_ATL10_default_varlist():
    obs = is2ref._default_varlists("ATL10")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
        "seg_dist_x",
        "lead_height",
        "lead_length",
        "beam_fb_height",
        "beam_fb_length",
        "beam_fb_confidence",
        "beam_fb_quality_flag",
        "height_segment_height",
        "height_segment_length_seg",
        "height_segment_ssh_flag",
        "height_segment_type",
        "height_segment_confidence",
    ]
    assert obs == expected


def test_ATL11_default_varlist():
    obs = is2ref._default_varlists("ATL11")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
        "h_corr",
        "h_corr_sigma",
        "h_corr_sigma_systematic",
        "quality_summary",
    ]
    assert obs == expected


def test_unsupported_default_varlist():
    obs = is2ref._default_varlists("ATL999")
    expected = [
        "delta_time",
        "latitude",
        "longitude",
    ]
    assert obs == expected


# #################### gt2spot tests #################################


def test_gt2spot_sc_orient_1():
    # gt1l
    obs = is2ref.gt2spot("gt1l", 1)
    expected = 6
    assert obs == expected

    # gt1r
    obs = is2ref.gt2spot("gt1r", 1)
    expected = 5
    assert obs == expected

    # gt2l
    obs = is2ref.gt2spot("gt2l", 1)
    expected = 4
    assert obs == expected

    # gt2r
    obs = is2ref.gt2spot("gt2r", 1)
    expected = 3
    assert obs == expected

    # gt3l
    obs = is2ref.gt2spot("gt3l", 1)
    expected = 2
    assert obs == expected

    # gt3r
    obs = is2ref.gt2spot("gt3r", 1)
    expected = 1
    assert obs == expected


def test_gt2spot_sc_orient_0():
    # gt1l
    obs = is2ref.gt2spot("gt1l", 0)
    expected = 1
    assert obs == expected

    # gt1r
    obs = is2ref.gt2spot("gt1r", 0)
    expected = 2
    assert obs == expected

    # gt2l
    obs = is2ref.gt2spot("gt2l", 0)
    expected = 3
    assert obs == expected

    # gt2r
    obs = is2ref.gt2spot("gt2r", 0)
    expected = 4
    assert obs == expected

    # gt3l
    obs = is2ref.gt2spot("gt3l", 0)
    expected = 5
    assert obs == expected

    # gt3r
    obs = is2ref.gt2spot("gt3r", 0)
    expected = 6
    assert obs == expected
