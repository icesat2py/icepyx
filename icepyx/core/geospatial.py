import geopandas as gpd
from shapely.geometry import Polygon


# DevGoal: need to update the spatial_extent docstring to describe coordinate order for input

def geodataframe(extent_type, spatial_extent, file=False):
    """
    Return a geodataframe of the spatial extent

    Parameters
    ----------
    extent_type : string
        One of 'bounding_box' or 'polygon', indicating what type of input the spatial extent is
    TODO: FIX THIS COMMENT SO THE WARNING GOES AWAY
    spatial_extent : string
        A string of the spatial extent. If file is False, the string should be a
        list of coordinates in decimal degrees of [lower-left-longitude,
        lower-left-latitute, upper-right-longitude, upper-right-latitude] or
        [longitude1, latitude1, longitude2, latitude2, ... longitude_n,latitude_n, longitude1,latitude1].

        If file is True, the string is the full file path and filename to the
        file containing the desired spatial extent.

    file : boolean, default False
        Indication for whether the spatial_extent string is a filename or coordinate list

    See Also
    --------
    icepyx.Query

    Examples
    --------
    >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
    >>> gdf = geodataframe(reg_a.extent_type, reg_a._spat_extent)
    >>> gdf.geometry
    0    POLYGON ((-55.00000 68.00000, -55.00000 71.000...
    Name: geometry, dtype: geometry
    """

    if extent_type == "bounding_box":
        boxx = [
            spatial_extent[0],
            spatial_extent[0],
            spatial_extent[2],
            spatial_extent[2],
            spatial_extent[0],
        ]
        boxy = [
            spatial_extent[1],
            spatial_extent[3],
            spatial_extent[3],
            spatial_extent[1],
            spatial_extent[1],
        ]
        # DevGoal: check to see that the box is actually correctly constructed; have not checked actual location of test coordinates
        # TODO: "spatial" (in validate_inputs) needs a "check_bounding_box" method.
        # TODO: Make sure there is a test case that ensures this gdf is constructed as expected (correct coords, order, etc.)
        gdf = gpd.GeoDataFrame(geometry=[Polygon(list(zip(boxx, boxy)))])

    # DevGoal: Currently this if/else within this elif are not tested...
    # DevGoal: the crs setting and management needs to be improved

    #extent_type is a polygon, file is false

    elif extent_type == "polygon" and file == False:
        # DevGoal: look into when/if this if is even called.
        # I think all the incoming spatial_extents without a file will be floats...

        # DEL: I don't think this if is ever used, so long as the spatial extent always comes in as a list of floats

        # if isinstance(spatial_extent,str):
        #     print('this string instance is needed')
        #     spat_extent = spatial_extent.split(',')
        #     spatial_extent_geom = Polygon(zip(spat_extent[0::2], spat_extent[1::2]))

        # if spatial_extent is already a Polygon
        if isinstance(spatial_extent, Polygon):
            spatial_extent_geom = spatial_extent

        # else, spatial_extent must be a list of floats (or list of tuples of floats)
        else:
            spatial_extent_geom = Polygon(
                # syntax of dbl colon is- "start:stop:steps"
                # 0::2 = start at 0, grab every other coord after
                # 1::2 = start at 1, grab every other coord after
                zip(spatial_extent[0::2], spatial_extent[1::2])
            )  # spatial_extent
        # TODO: check if the crs param should always just be epsg:4326 for everything OR if it should be a parameter
        gdf = gpd.GeoDataFrame(
            index=[0], crs="epsg:4326", geometry=[spatial_extent_geom]
        )

    # If extent_type is a polygon AND from a file, create a geopandas geodataframe from it
    # DevGoal: Currently this elif isn't tested...
    elif extent_type == "polygon" and file == True:
        gdf = gpd.read_file(spatial_extent)

    else:
        raise TypeError(
            "Your spatial extent type is not an accepted input and a geodataframe cannot be constructed"
        )
        # TODO: Get this working again
        # DevNote: can't get test for this else to pass if print the extent_type in the string...
        # raise TypeError("Your spatial extent type (" + extent_type + ") is not an accepted input and a geodataframe cannot be constructed")

    return gdf
