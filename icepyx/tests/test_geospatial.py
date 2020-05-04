import pytest
import warnings
import geopandas as gpd


import icepyx.core.geospatial as geospatial

########## geodataframe ##########
def test_gdf_from_bbox():
    obs = geospatial.geodataframe('bounding_box',[-55, 68, -48, 71])
    geom = gpd.points_from_xy([-55, -55, -48, -48, -55], [68, 71, 71, 68, 68])
    exp = gpd.GeoDataFrame(geometry=geom)
    assert obs == exp


#TestQuestions: 1) Do these need to be tested?
#2) Is the best way to test them with lengthy inputs and seeing if the gdfs are the same?
# def test_gdf_from_strpoly():

# def test_gdf_from_filepoly():


def test_bad_extent_input():
    ermsg = "Your spatial extent type (polybox) is not an accepted input and a geodataframe cannot be constructed"
    with pytest.raises(TypeError, match=ermsg):
        geospatial.geodataframe('polybox',[1,2,3,4])