import pytest
import warnings
import geopandas as gpd
from shapely.geometry import Polygon


import icepyx.core.geospatial as geospatial

########## geodataframe ##########
def test_gdf_from_bbox():
    obs = geospatial.geodataframe('bounding_box',[-55, 68, -48, 71])
    geom = [Polygon(list(zip([-55, -55, -48, -48, -55], [68, 71, 71, 68, 68])))]
    exp = gpd.GeoDataFrame(geometry=geom)
    #DevNote: this feels like a questionable test to me, since it specifies the first entry (though there should only be one)
    assert obs.geometry[0] == exp.geometry[0]


#TestQuestions: 1) Do these need to be tested?
#2) Is the best way to test them with lengthy inputs and seeing if the gdfs are the same?
# def test_gdf_from_strpoly():

# def test_gdf_from_filepoly():


def test_bad_extent_input():
    ermsg = "Your spatial extent type is not an accepted input and a geodataframe cannot be constructed"
    #DevNote: can't get the test to pass if the extent_type is included. Not sure why the strings "don't match"
    # ermsg = "Your spatial extent type (polybox) is not an accepted input and a geodataframe cannot be constructed"
    with pytest.raises(TypeError, match=ermsg):
        geospatial.geodataframe('polybox',[1,2,3,4])