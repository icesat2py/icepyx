import pytest
import warnings
import datetime as dt
import numpy as np
import icepyx.core.validate_inputs_spatial as sp


#################### "General" Tests ###################################################################

'''
Test properties/"getters"
'''
def test_extent_type_property():


def test_spatial_extent_property():


def test_geom_file_property():

################## End General Tests ##################################################################
'''
polygon
create a test for each “possible input type”
make sure the expected “type”/output is created
make sure that bad lats/longs are handled
outside of real lat/long values
make sure that too few inputs throws an error
make sure polygons are automatically closed
make sure the resultant polygon is correct (first point == last point)
make sure that a warning is given to the user
make sure that the extent_type is correct on output
polygon file
create a test for each “possible input file type”
kml, shp, gpkg
make sure bad input file types throw the correct error
make sure files with multiple polygons throw a warning and only select the first polygon
make sure the expected “type”/output is created
make sure input files that do not exist throw an error
make sure the extent_type is correct on output
make sure an error is thrown if the resultant extent type isn’t a “good type” 



'''

# ######### "Bounding Box" input tests ################################################################################


def test_intlist_bbox():
    """
    Bounding box test w/ a List of valid Int inputs.
    * tests that expected output is correct
    * tests that extent_type is correct

    """
    # initialize Spatial object;
    # it should call validate_spatial function correctly

    intlist_bbox = sp.Spatial([-64, 66, -55, 72])
    assert intlist_bbox.extent_type == "bounding_box"
    assert intlist_bbox.extent_file is None
    assert intlist_bbox.spatial_extent == [-64, 66, -55, 72]


def test_floatlist_bbox():
    floatlist_bbox = sp.Spatial([-64.2, 66.2, -55.5, 72.5])
    assert floatlist_bbox.extent_type == "bounding_box"
    assert floatlist_bbox.extent_file is None
    assert floatlist_bbox.spatial_extent == [-64.2, 66.2, -55.5, 72.5]


def test_numpyfloatarray_bbox():
    npfloat_bbox = sp.Spatial(np.array([-64.2, 66.2, -55.5, 72.5]))
    assert npfloat_bbox.extent_type == "bounding_box"
    assert npfloat_bbox.extent_file is None
    assert npfloat_bbox.spatial_extent == [-64.2, 66.2, -55.5, 72.5]


def test_numpyfloatlist_bbox():
    npfloatlist_bbox = sp.Spatial(list(np.array([-64.2, 66.2, -55.5, 72.5])))
    assert npfloatlist_bbox.extent_type == "bounding_box"
    assert npfloatlist_bbox.extent_file is None
    assert npfloatlist_bbox.spatial_extent == [-64.2, 66.2, -55.5, 72.5]


def test_too_few_bbox_points():

def test_too_many_bbox_points():


def test_invalid_low_latitude_1_bbox():

def test_invalid_high_latitude_1_bbox():

def test_invalid_low_latitude_3_bbox():

def test_invalid_high_latitude_3_bbox():


def test_invalid_low_longitude_0_bbox():

def test_invalid_high_longitude_0_bbox():

def test_invalid_low_longitude_2_bbox():

def test_invalid_high_longitude_2_bbox():


def test_diff_sign_lowleft_lt_upright_longitude_bbox():

def test_same_sign_lowleft_gt_upright_longitude_bbox():

def test_same_sign_lowleft_gt_upright_latitude_bbox():







#def test_too_few_poly_points():