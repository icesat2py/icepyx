import datetime as dt
import os
import warnings
import geopandas as gpd
import numpy as np

import icepyx.core.APIformatting as apifmt
import icepyx.core.geospatial as geospatial



class Spatial:

    def __init__(self, spatial_extent=None, extent_type=None):
      # TODO: VALIDATE EXTENT UPON CONSTRUCTION? figure out if thats what you should do
      # TODO: Ask/check if these "local variable" names must be diff. than in other files
      self._spatial_ext = spatial_extent
      self._ext_type = extent_type

    def __str__(self):
        return "Extent type: {0} \nCoordinates: {1}".format(self._ext_type, self._spatial_ext)

    #TODO: See if "property" getter functions are required (seems like they'll be redundant with Query)
    #@property
    #def spatial_extent(self):
    #@property
    #def extent_type(self):
    '''
        doesn't return anything; should be interfacing with a spatial_extent object
    '''
    def validate_bounding_box(self, spatial_extent):

            # Latitude must be between -90 and 90 (inclusive); check for this here
            assert -90 <= spatial_extent[1] <= 90, "Invalid latitude value (must be between -90 and 90, inclusive)"
            assert -90 <= spatial_extent[3] <= 90, "Invalid latitude value (must be between -90 and 90, inclusive)"

            # tighten these ranges depending on actual allowed inputs
            # TODO: inquire about this; see if we know the "actual allowed inputs" and if this can be fixed now

            assert -180 <= spatial_extent[0] <= 180, "Invalid longitude value (must be between -180 and 180, inclusive)"
            assert -180 <= spatial_extent[2] <= 180, "Invalid longitude value (must be between -180 and 180, inclusive)"

            # If the longitude's signs differ...
            if np.sign(spatial_extent[0]) != np.sign(spatial_extent[2]):
                # If the lower left longitude is less than the upper right longitude, throw an error
                assert (spatial_extent[0] >= spatial_extent[2]), "Invalid bounding box longitudes"

            # Else, if longitude signs are the same...
            else:
                # If the lower left longitude is greater than the upper right longitude, throw an error
                assert (spatial_extent[0] <= spatial_extent[2]), "Invalid bounding box longitudes"

            # If the lower left latitude is greater than the upper right latitude, throw an error
            assert (spatial_extent[1] <= spatial_extent[3]), "Invalid bounding box latitudes"

            # initialize _spat_extent "private variable"; it's just spatial_extent's longs/lats but as floats
            self._spatial_ext = [float(x) for x in spatial_extent]

            # we now know extent_type is "bounding_box" so set this accordingly
            self._ext_type = "bounding_box"

    def validate_polygon_pairs(self, spatial_extent):
        # Check to make sure all elements of spatial_extent are coordinate pairs; if not, raise an error
        if any(len(i) != 2 for i in spatial_extent):
            raise ValueError("Each element in spatial_extent should be a list or tuple of length 2")

        # If there are less than 4 vertices, raise an error
        assert (len(spatial_extent) >= 4), "Your spatial extent polygon has too few vertices"

        # TODO: Write unit test for this method.
        if (spatial_extent[0][0] != spatial_extent[-1][0]) or (spatial_extent[0][1] != spatial_extent[-1][1]):

            # Throw a warning
            warnings.warn("WARNING: Polygon's first and last point's coordinates differ,"
                          " closing the polygon automatically.")
            # Add starting long/lat to end
            if isinstance(spatial_extent, list):
                # use list.append() method
                spatial_extent.append(spatial_extent[0])

            elif isinstance(spatial_extent, np.ndarray):
                # use np.insert() method
                spatial_extent = np.insert(spatial_extent, len(spatial_extent), spatial_extent[0])

        polygon = (",".join([str(c) for xy in spatial_extent for c in xy])).split(",")

        # set extent_type to polygon
        self._ext_type = "polygon"

        # make all elements of polygon floats
        polygon = [float(i) for i in polygon]

        # create a geodataframe object from polygon
        gdf = geospatial.geodataframe(self._ext.type, polygon, file=False)
        self._spatial_ext = gdf.iloc[0].geometry

        # _spat_extent = polygon
        # extent_type = 'polygon'
        # TODO: Check if this DevGoal is still ongoing
        # #DevGoal: properly format this input type (and any polygon type) so that it is clockwise (and only contains 1 pole)!!
        # warnings.warn("this type of input is not yet well handled and you may not be able to find data")

    def validate_polygon_list(self, spatial_extent):
        # user-entered polygon as a single list of lon and lat coordinates

        assert (
                len(spatial_extent) >= 8
        ), "Your spatial extent polygon has too few vertices"
        assert (
                len(spatial_extent) % 2 == 0
        ), "Your spatial extent polygon list should have an even number of entries"

        # TODO: Make polygon close automatically + throw warning
        # TODO: Test this method
        # assert (spatial_extent[0] == spatial_extent[-2]), "Starting longitude doesn't match ending longitude"
        # assert (spatial_extent[1] == spatial_extent[-1] ), "Starting latitude doesn't match ending latitude"

        warnings.warn("WARNING: Polygon's first and last point's coordinates differ,"
                      " closing the polygon automatically.")
        # Add starting long/lat to end
        if isinstance(spatial_extent, list):
            # use list.append() method
            spatial_extent.append(spatial_extent[0])
            spatial_extent.append(spatial_extent[1])

        elif isinstance(spatial_extent, np.ndarray):
            # use np.insert() method
            spatial_extent = np.insert(spatial_extent, len(spatial_extent), spatial_extent[0])
            spatial_extent = np.insert(spatial_extent, len(spatial_extent), spatial_extent[1])

        extent_type = "polygon"
        polygon = [float(i) for i in spatial_extent]

        gdf = geospatial.geodataframe(extent_type, polygon, file=False)
        _spat_extent = gdf.iloc[0].geometry

        # _spat_extent = polygon




    def validate_polygon_file(self, spatial_extent):
        # Check if the filename path exists; if not, throw an error
        # TODO: Trigger this error and see what it looks like
        assert os.path.exists(spatial_extent), "Check that the path and filename of your geometry file are correct"

        # DevGoal: more robust polygon inputting (see Bruce's code):
        # correct for clockwise/counterclockwise coordinates, deal with simplification, etc.

        # If the filename has extension kml, shp, or gpkg:
        if spatial_extent.split(".")[-1] in ["kml", "shp", "gpkg"]:
            extent_type = "polygon"
            gdf = geospatial.geodataframe(extent_type, spatial_extent, file=True)
            # print(gdf.iloc[0].geometry)
            # DevGoal: does the below line mandate that only the first polygon will be read?
            # Perhaps we should require files containing only one polygon?

            # RAPHAEL - It only selects the first polygon if there are multiple.
            # Unless we can supply the CMR params with muliple polygon inputs
            # we should probably req a single polygon.
            # TODO: Require a single polygon OR throw a warning that only the first polygon will be selected

            _spat_extent = gdf.iloc[0].geometry

            # _spat_extent = apifmt._fmt_polygon(spatial_extent)

            _geom_filepath = spatial_extent
        # Filename has an invalid extension type; raise a TypeError
        else:
            raise TypeError("Input spatial extent file must be a kml, shp, or gpkg")

    def validate_extent(self, spatial_extent):
        """
        Validate the input spatial extent and return the needed parameters to the query object.

        spatial_extent : expects one of the following:
            * list of coordinates (stored in a list of strings, list of numerics, list of tuples, OR np.ndarray) as one of:
                * bounding box
                    * provided in the order: [lower-left-longitude, lower-left-latitude,
                                             upper-right-longitude, upper-right-latitude].)
                * polygon
                    * provided as coordinate pairs in decimal degrees as one of:
                        * [(longitude1, latitude1), (longitude2, latitude2), ...
                          ... (longitude_n,latitude_n), (longitude1,latitude1)]
                        * [longitude1, latitude1, longitude2, latitude2, ... longitude_n,latitude_n, longitude1,latitude1].
                    * your list must contain at least four points, where the first and last are identical.
                        * TODO: Make polygon close automatically if the first/last points aren't identical, throw warn
            * string representing a geospatial polygon file (kml, shp, gpkg)
                * full file path
                * recommended for file to only contain 1 polygon; if multiple, only selects first polygon rn
        """
        scalar_types = (int, float, np.int64)

        # Check if spatial_extent is a bounding box or a polygon (list of coords)
        # Check if spatial_extent is a "list" or an "numpy.ndarray"

        # NOTE: I think that the input is assumed to be "strings"; thats why we must cast to float later
        # This may also "flatten" the array so geospatial.geodataframe will work

        if isinstance(spatial_extent, (list, np.ndarray)):
            # bounding box
            if len(spatial_extent) == 4 and all(isinstance(i, scalar_types) for i in spatial_extent):
                self.validate_bounding_box(self, spatial_extent)

            # user-entered polygon as list of lon, lat coordinate pairs

            # (NOTE: The all() function returns True if all items in an iterable are true, otherwise it returns False.)

            # TODO: Write this "check" as a separate function? maybe do the same with bounding box?
            elif all(type(i) in [list, tuple, np.ndarray] for i in spatial_extent) \
                    and all(all(isinstance(i[j], scalar_types) for j in range(len(i))) for i in spatial_extent):
                self.validate_polygon_pairs(self, spatial_extent)

            elif all(isinstance(i, scalar_types) for i in spatial_extent):
                # DevGoal: write a test for this?
                self.validate_polygon_pairs(self, spatial_extent)
            else:
                raise ValueError(
                    "Your spatial extent does not meet minimum input criteria or the input format is not correct"
                )

        # TODO: See if this is still required with spatial structure
        # try:
        #    del _geom_filepath
        # except:
        #    UnboundLocalError

        # DevGoal: revisit this section + geospatial.geodataframe.
        # There might be some good ways to combine the functionality in these checks with that

        # Else if spatial_extent is a string (i.e. a (potential) filename)
        elif isinstance(spatial_extent, str):
            self.validate_polygon_file(self, spatial_extent)

        # DevGoal: currently no specific test for this if statement...
        if "_geom_filepath" not in locals():
            _geom_filepath = None

        # TODO: Check if all of these returns are still required; I think they get set as
        # properties of Spatial type so they are no longer needed.
        # return extent_type, _spat_extent, _geom_filepath

