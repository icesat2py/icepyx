import os
import warnings
import numpy as np

import icepyx.core.APIformatting as apifmt
import icepyx.core.geospatial as geospatial


def validate_bounding_box(spatial_extent):

    # Latitude must be between -90 and 90 (inclusive); check for this here
    assert -90 <= spatial_extent[1] <= 90, "Invalid latitude value (must be between -90 and 90, inclusive)"
    assert -90 <= spatial_extent[3] <= 90, "Invalid latitude value (must be between -90 and 90, inclusive)"

    # tighten these ranges depending on actual allowed inputs
    # TODO: inquire about this; see if we know the "actual allowed inputs" and if this can be fixed
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
    spatial_extent = [float(x) for x in spatial_extent]

    return "bounding_box", spatial_extent, None


def validate_polygon_pairs(spatial_extent):
    # Check to make sure all elements of spatial_extent are coordinate pairs; if not, raise an error
    if any(len(i) != 2 for i in spatial_extent):
        raise ValueError("Each element in spatial_extent should be a list or tuple of length 2")

    # If there are less than 4 vertices, raise an error
    assert (len(spatial_extent) >= 4), "Your spatial extent polygon has too few vertices"

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

    # make all elements of polygon floats
    polygon = [float(i) for i in polygon]

    # create a geodataframe object from polygon
    gdf = geospatial.geodataframe("polygon", polygon, file=False)
    spatial_extent = gdf.iloc[0].geometry

    # TODO: Check if this DevGoal is still ongoing

    # #DevGoal: properly format this input type (and any polygon type)
    # so that it is clockwise (and only contains 1 pole)!!
    # warnings.warn("this type of input is not yet well handled and you may not be able to find data")

    return "polygon", spatial_extent, None


def validate_polygon_list(spatial_extent):

    # user-entered polygon as a single list of lon and lat coordinates
    assert (
            len(spatial_extent) >= 8
    ), "Your spatial extent polygon has too few vertices"
    assert (
            len(spatial_extent) % 2 == 0
    ), "Your spatial extent polygon list should have an even number of entries"

    if (spatial_extent[0] != spatial_extent[-2]) or (spatial_extent[1] != spatial_extent[-1]):
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
    spatial_extent = gdf.iloc[0].geometry

    return "polygon", spatial_extent, None


def validate_polygon_file(spatial_extent):

    # Check if the filename path exists; if not, throw an error
    #print("print statements work \n")
    #print("SPATIAL EXTENT: " + spatial_extent + "\n")
    assert os.path.exists(spatial_extent), "Check that the path and filename of your geometry file are correct"

    # DevGoal: more robust polygon inputting (see Bruce's code):
    # correct for clockwise/counterclockwise coordinates, deal with simplification, etc.

    if spatial_extent.split(".")[-1] in ["kml", "shp", "gpkg"]:
        extent_type = "polygon"
        gdf = geospatial.geodataframe(extent_type, spatial_extent, file=True)

        # DevGoal: does the below line mandate that only the first polygon will be read?
        # Perhaps we should require files containing only one polygon?

        # RAPHAEL - It only selects the first polygon if there are multiple.
        # Unless we can supply the CMR params with muliple polygon inputs
        # we should probably req a single polygon.

        # TODO: Require a single polygon OR throw a warning that only the first polygon will be selected?

        gdf_result = gdf.iloc[0].geometry

        # _spat_extent = apifmt._fmt_polygon(spatial_extent)
        return "polygon", gdf_result, spatial_extent

    else:
        raise TypeError("Input spatial extent file must be a kml, shp, or gpkg")


class Spatial:

    def __init__(self, spatial_extent):
        """
              Validates input from "spatial_extent" argument, then creates a Spatial object with validated inputs
              as properties of the object.

              Parameters:

              spatial_extent : expects one of the following:
                  * list of coordinates
                   (stored in a list of strings, list of numerics, list of tuples, OR np.ndarray) as one of:
                      * bounding box
                          * provided in the order: [lower-left-longitude, lower-left-latitude,
                                                   upper-right-longitude, upper-right-latitude].)
                      * polygon
                          * provided as coordinate pairs in decimal degrees as one of:
                              * [(longitude1, latitude1), (longitude2, latitude2), ...
                                ... (longitude_n,latitude_n), (longitude1,latitude1)]
                              * [longitude1, latitude1, longitude2, latitude2,
                              ... longitude_n,latitude_n, longitude1,latitude1].
                          * NOTE: If the first and last coordinate pairs are NOT equal,
                          the polygon will be closed automatically (last point will be connected to the first point).
                  * string representing a geospatial polygon file (kml, shp, gpkg)
                      * full file path
                      * recommended for file to only contain 1 polygon; if multiple, only selects first polygon rn
              Properties:
                * _spat_ext: The validated/formatted input from spatial_extent,
                             represents coordinates of a polygon or bounding box.
                * _ext_type: The extent type of spatial_extent, one of: polygon, bounding_box
                * _geom_file: If spatial_extent was NOT a filename, this is None.
                              Else, it is the name of the file that _spat_ext is retrieved/validated from.
              """

        scalar_types = (int, float, np.int64)

        # Check if spatial_extent is a list of coordinates (bounding box or polygon)
        if isinstance(spatial_extent, (list, np.ndarray)):

            # bounding box
            if len(spatial_extent) == 4 and all(isinstance(i, scalar_types) for i in spatial_extent):
                self._ext_type, self._spatial_ext, self._geom_file = validate_bounding_box(spatial_extent)

            # polygon (as list of lon, lat coordinate pairs, in tuples)
            elif all(type(i) in [list, tuple, np.ndarray] for i in spatial_extent) \
                    and all(all(isinstance(i[j], scalar_types) for j in range(len(i))) for i in spatial_extent):
                self._ext_type, self._spatial_ext, self._geom_file = validate_polygon_pairs(spatial_extent)

            # polygon (as list of lon, lat coordinate pairs, single "flat" list)
            elif all(isinstance(i, scalar_types) for i in spatial_extent):
                self._ext_type, self._spatial_ext, self._geom_file = validate_polygon_list(spatial_extent)
            else:
                # TODO: Change this warning to be like "usage", tell user possible accepted input types
                raise ValueError(
                    "Your spatial extent does not meet minimum input criteria or the input format is not correct"
                )

        # Check if spatial_extent is a string (i.e. a (potential) filename)
        elif isinstance(spatial_extent, str):
            self._ext_type, self._spatial_ext, self._geom_file = validate_polygon_file(spatial_extent)

    def __str__(self):
        if self.extent_file is not None:
            return "Extent type: {0}\nSource file: {1}\nCoordinates: {2}".format(self._ext_type,
                                                                                 self._geom_file, self._spatial_ext)
        else:
            return "Extent type: {0} \nCoordinates: {1}".format(self._ext_type, self._spatial_ext)

    @property
    def spatial_extent(self):
        return self._spatial_ext

    @property
    def extent_type(self):
        return self._ext_type

    @property
    def extent_file(self):
        return self._geom_file
