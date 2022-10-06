import datetime as dt
import geopandas as gpd
import numpy as np
import os
from pathlib import Path
import pytest
from shapely.geometry import Polygon
import warnings

import icepyx.core.spatial as spat


# ######### "Bounding Box" input tests ################################################################################
# (Note that these ALSO test the @property functions for the class for bounding boxes)


def test_intlist_bbox():
    """
    Bounding box test w/ a List of valid Int inputs.
    * tests that expected output is correct
    * tests that _ext_type is correct

    """
    # initialize Spatial object;
    # it should call validate_spatial function correctly

    intlist_bbox = spat.Spatial([-64, 66, -55, 72])
    assert intlist_bbox._ext_type == "bounding_box"
    assert intlist_bbox._geom_file is None
    assert intlist_bbox.extent == [-64, 66, -55, 72]


def test_floatlist_bbox():
    floatlist_bbox = spat.Spatial([-64.2, 66.2, -55.5, 72.5])
    assert floatlist_bbox._ext_type == "bounding_box"
    assert floatlist_bbox._geom_file is None
    assert floatlist_bbox.extent == [-64.2, 66.2, -55.5, 72.5]


def test_numpyfloatarray_bbox():
    npfloat_bbox = spat.Spatial(np.array([-64.2, 66.2, -55.5, 72.5]))
    assert npfloat_bbox._ext_type == "bounding_box"
    assert npfloat_bbox._geom_file is None
    assert npfloat_bbox.extent == [-64.2, 66.2, -55.5, 72.5]


def test_numpyfloatlist_bbox():
    npfloatlist_bbox = spat.Spatial(list(np.array([-64.2, 66.2, -55.5, 72.5])))
    assert npfloatlist_bbox._ext_type == "bounding_box"
    assert npfloatlist_bbox._geom_file is None
    assert npfloatlist_bbox.extent == [-64.2, 66.2, -55.5, 72.5]


def test_intlist_with0_bbox():
    npfloatlist_bbox = spat.Spatial(list(np.array([0, -80, 90, -60])))
    assert npfloatlist_bbox._ext_type == "bounding_box"
    assert npfloatlist_bbox._geom_file is None
    assert npfloatlist_bbox.extent == [0, -80, 90, -60]


# ########## Bounding Box Assertion Error tests #############################################
# (input for all of these tests is bad; ensuring the spatial class catches this)


def test_too_few_bbox_points():
    with pytest.raises(AssertionError):
        too_few_bbox_points = spat.Spatial([-64.2, 66.2, -55.5])


def test_too_many_bbox_points():
    with pytest.raises(AssertionError):
        too_many_bbox_points = spat.Spatial([-64.2, 66.2, -55.5, 72.5, 0])


def test_invalid_low_latitude_1_bbox():
    with pytest.raises(AssertionError):
        low_lat_1_bbox = spat.Spatial([-64.2, -90.2, -55.5, 72.5])


def test_invalid_high_latitude_1_bbox():
    with pytest.raises(AssertionError):
        high_lat_1_bbox = spat.Spatial([-64.2, 90.2, -55.5, 72.5])


def test_invalid_low_latitude_3_bbox():
    with pytest.raises(AssertionError):
        low_lat_3_bbox = spat.Spatial([-64.2, 66.2, -55.5, -90.5])


def test_invalid_high_latitude_3_bbox():
    with pytest.raises(AssertionError):
        high_lat_3_bbox = spat.Spatial([-64.2, 66.2, -55.5, 90.5])


def test_invalid_low_longitude_0_bbox():
    with pytest.raises(AssertionError):
        low_lon_0_bbox = spat.Spatial([-180.2, 66.2, -55.5, 72.5])


def test_invalid_high_longitude_0_bbox():
    with pytest.raises(AssertionError):
        high_lon_0_bbox = spat.Spatial([180.2, 66.2, -55.5, 72.5])


def test_invalid_low_longitude_2_bbox():
    with pytest.raises(AssertionError):
        low_lon_2_bbox = spat.Spatial([-64.2, 66.2, -180.5, 72.5])


def test_invalid_high_longitude_2_bbox():
    with pytest.raises(AssertionError):
        high_lon_2_bbox = spat.Spatial([-64.2, 66.2, 180.5, 72.5])


def test_same_sign_lowleft_gt_upright_latitude_bbox():
    with pytest.raises(AssertionError):
        lat_ll_gt_ur_ss_bbox = spat.Spatial([-64.2, 72.5, -55.5, 66.2])


def test_bad_values_bbox():
    with pytest.raises(ValueError):
        bad_input = spat.Spatial(["a", "b", "c", "d"])


# ############### END BOUNDING BOX TESTS ################################################################

# ######### "Polygon" input tests (NOT FROM FILE) ######################################################


def test_list_pairs_polygon():
    poly_list_pair = spat.Spatial(
        [[-55, 68], [-55, 71], [-48, 71], [-48, 68], [-55, 68]]
    )
    expected_poly_list_pair = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_list_pair._ext_type == "polygon"
    assert poly_list_pair._geom_file is None
    assert poly_list_pair.extent == expected_poly_list_pair


def test_tuple_latlon_pairs():
    poly_tuple_pair = spat.Spatial(
        [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
    )
    expected_poly_tuple_pair = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_tuple_pair._ext_type == "polygon"
    assert poly_tuple_pair._geom_file is None
    assert poly_tuple_pair.extent == expected_poly_tuple_pair


def test_intlist_latlon_coords():
    poly_list = spat.Spatial([-55, 68, -55, 71, -48, 71, -48, 68, -55, 68])
    expected_poly_list = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_list._ext_type == "polygon"
    assert poly_list._geom_file is None
    assert poly_list.extent == expected_poly_list


def test_floatlist_latlon_coords():
    poly_float_list = spat.Spatial(
        [-55.0, 68.7, -55.0, 71, -48, 71, -48, 68.7, -55.0, 68.7]
    )
    expected_poly_float_list = [
        -55.0,
        68.7,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.7,
        -55.0,
        68.7,
    ]

    assert poly_float_list._ext_type == "polygon"
    assert poly_float_list._geom_file is None
    assert poly_float_list.extent == expected_poly_float_list


# numpy array tests


def test_numpy_list_pairs_polygon():
    poly_list_pair = spat.Spatial(
        np.array([[-55, 68], [-55, 71], [-48, 71], [-48, 68], [-55, 68]])
    )
    expected_poly_list_pair = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_list_pair._ext_type == "polygon"
    assert poly_list_pair._geom_file is None
    assert poly_list_pair.extent == expected_poly_list_pair


def test_numpy_tuple_latlon_pairs():
    poly_tuple_pair = spat.Spatial(
        np.array([(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)])
    )
    expected_poly_tuple_pair = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_tuple_pair._ext_type == "polygon"
    assert poly_tuple_pair._geom_file is None
    assert poly_tuple_pair.extent == expected_poly_tuple_pair


def test_numpy_intlist_latlon_coords():
    poly_list = spat.Spatial(np.array([-55, 68, -55, 71, -48, 71, -48, 68, -55, 68]))
    expected_poly_list = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_list._ext_type == "polygon"
    assert poly_list._geom_file is None
    assert poly_list.extent == expected_poly_list


# ########## Polygon Assertion Error tests ############################################################
# (input for all of these tests is bad; ensuring the spatial class catches this)


def test_odd_num_lat_long_list_poly_throws_error():
    with pytest.raises(AssertionError):
        bad_input = spat.Spatial([-55, 68, -55, 71, -48, 71, -48, 68, -55])


def test_wrong_num_lat_long_tuple_poly_throws_error():
    with pytest.raises(ValueError):
        bad_input = spat.Spatial(
            [(-55, 68, 69), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
        )


def test_bad_value_types_poly():
    with pytest.raises(ValueError):
        bad_input = spat.Spatial(["a", "b", "c", "d", "e"])


# ###################### Automatically Closed Polygon Tests ###########################################################


def test_poly_tuple_latlon_pairs_auto_close():
    poly_tuple_pair = spat.Spatial([(-55, 68), (-55, 71), (-48, 71), (-48, 68)])
    expected_poly_tuple_pair = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_tuple_pair._ext_type == "polygon"
    assert poly_tuple_pair._geom_file is None
    assert poly_tuple_pair.extent == expected_poly_tuple_pair


def test_poly_list_auto_close():
    poly_list = spat.Spatial([-55, 68, -55, 71, -48, 71, -48, 68])
    expected_poly_list = [
        -55.0,
        68.0,
        -55.0,
        71.0,
        -48.0,
        71.0,
        -48.0,
        68.0,
        -55.0,
        68.0,
    ]

    assert poly_list._ext_type == "polygon"
    assert poly_list._geom_file is None
    assert poly_list.extent == expected_poly_list


# ###################### END POLYGON NO FILE TESTS ####################################################################
# ######### Geom File Input Tests ######################################################


def test_poly_file_simple_one_poly():

    poly_from_file = spat.Spatial(
        str(
            Path(
                "./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg"
            ).resolve()
        )
    )

    print(poly_from_file.extent)
    expected_poly = [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]

    assert poly_from_file._ext_type == "polygon"
    assert poly_from_file._geom_file is not None
    assert poly_from_file._geom_file == str(
        Path(
            "./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg"
        ).resolve()
    )
    assert poly_from_file.extent == expected_poly


"""
TODO: test files with multiple polygons throw a warning and only select the first polygon
"""

# ########## Geom File Assertion Error tests ############################################################

# (input for all of these tests is bad; ensuring the spatial class catches this)


def test_bad_poly_inputfile_name_throws_error():
    with pytest.raises(AssertionError):
        bad_input = spat.Spatial("bad_filename.gpkg")


def test_bad_poly_inputfile_type_throws_error():
    with pytest.raises(TypeError):
        bad_input = spat.Spatial(str(Path("./icepyx/tests/test_read.py").resolve()))


########## geodataframe ##########


def test_gdf_from_one_bbox():

    obs = spat.geodataframe("bounding_box", [-55, 68, -48, 71])
    geom = [Polygon(list(zip([-55, -55, -48, -48, -55], [68, 71, 71, 68, 68])))]
    exp = gpd.GeoDataFrame(geometry=geom)

    # print(obs.geometry[0])
    # print(exp.geometry[0])

    # print(exp)
    # DevNote: this feels like a questionable test to me, since it specifies the first entry (though there should only be one)

    assert obs.geometry[0].equals(exp.geometry[0])


def test_gdf_from_multi_bbox():
    obs = spat.geodataframe("bounding_box", [-55, 68, -48, 71])
    geom = [Polygon(list(zip([-55, -55, -48, -48, -55], [68, 71, 71, 68, 68])))]
    exp = gpd.GeoDataFrame(geometry=geom)

    print(obs.geometry[0])
    print(exp.geometry[0])
    # DevNote: this feels like a questionable test to me, since it specifies the first entry (though there should only be one)
    assert obs.geometry[0].equals(exp.geometry[0])


# TestQuestions: 1) Do these need to be tested?
# 2) Is the best way to test them with lengthy inputs and seeing if the gdfs are the same?

# def test_gdf_from_strpoly_one_simple():

# def test_gdf_from_strpoly_multi_simple():

# def test_gdf_from_strpoly_one_complex():

# def test_gdf_from_filepoly_one_simple():

# def test_gdf_from_filepoly_one_complex():

# def test_gdf_from_filepoly_multi_simple():


def test_bad_extent_input():
    ermsg = "Your spatial extent type is not an accepted input and a geodataframe cannot be constructed"
    # DevNote: can't get the test to pass if the extent_type is included. Not sure why the strings "don't match"
    # ermsg = "Your spatial extent type (polybox) is not an accepted input and a geodataframe cannot be constructed"
    with pytest.raises(TypeError, match=ermsg):
        spat.geodataframe("polybox", [1, 2, 3, 4])


# ###################### END GEOM FILE INPUT TESTS ####################################################################
# ######### Dateline Crossing Tests ######################################################

# TODO: Fill in tests here (all are templated)
def test_bbox_crosses_dateline():
    bboxes = [
        [-55.5, 66.2, -64.2, 72.5],
        [1, -71, -1, -70],
    ]

    for bbox in bboxes:
        obs = spat.check_dateline("bounding_box", bbox)
        exp = True
        assert exp == obs


def test_bbox_not_crosses_dateline():
    bboxes = [
        [-64.2, 66.2, 55.5, 72.5],
        [-55, 68, -48, 71],
        [-1, -71, 1, -70],
    ]
    for bbox in bboxes:
        obs = spat.check_dateline("bounding_box", bbox)
        exp = False
        assert exp == obs


def test_poly_wrong_input():
    with pytest.raises(AssertionError):
        tuplelist = spat.check_dateline(
            "polygon",
            [[160, -45], [160, -40], [-170, -39], [-128, -40], [-128, -45], [160, -45]],
        )


def test_poly_crosses_dateline():
    obs = spat.check_dateline(
        "polygon", [160, -45, 160, -40, -170, -39, -128, -40, -128, -45, 160, -45]
    )
    exp = True
    assert exp == obs


# Note: users must manually specify their region crosses the dateline for regions spanning >90 longitude
def test_poly_not_crosses_dateline():
    obs = spat.check_dateline(
        "polygon", [-55, 68, -55, 71, -48, 71, -47, 70, -48, 68, -55, 68]
    )
    exp = False
    assert exp == obs
