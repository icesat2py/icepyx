import datetime as dt
import os
import warnings
import geopandas as gpd
import numpy as np

import icepyx.core.APIformatting as apifmt
import icepyx.core.geospatial as geospatial


def prod_version(latest_vers, version):
    """
    Check if the submitted product version is valid, and warn the user if a newer version is available.
    """
    if version is None:
        vers = latest_vers
    else:
        if isinstance(version, str):
            assert int(version) > 0, "Version number must be positive"
            vers_length = 3
            vers = version.zfill(vers_length)
        else:
            raise TypeError("Please enter the version number as a string")

        if int(vers) < int(latest_vers):
            warnings.filterwarnings("always")
            warnings.warn("You are using an old version of this product")

    return vers


def cycles(cycle):
    """
    Check if the submitted cycle is valid, and warn the user if not available.
    """
    cycle_length = 2
    # number of GPS seconds between the GPS epoch and ATLAS SDP epoch
    atlas_sdp_gps_epoch = 1198800018.0
    # number of GPS seconds since the GPS epoch for first ATLAS data point
    atlas_gps_start_time = atlas_sdp_gps_epoch + 24710205.39202261
    epoch1 = dt.datetime(1980, 1, 6, 0, 0, 0)
    epoch2 = dt.datetime(1970, 1, 1, 0, 0, 0)
    # get the total number of seconds since the start of ATLAS and now
    delta_time_epochs = (epoch2 - epoch1).total_seconds()
    atlas_UNIX_start_time = atlas_gps_start_time - delta_time_epochs
    present_time = dt.datetime.now().timestamp()
    # divide total time by cycle length to get the maximum number of orbital cycles
    ncycles = np.ceil((present_time - atlas_UNIX_start_time) / (86400 * 91)).astype("i")
    all_cycles = [str(c + 1).zfill(cycle_length) for c in range(ncycles)]

    if cycle is None:
        return []
    else:
        if isinstance(cycle, str):
            assert int(cycle) > 0, "Cycle number must be positive"
            cycle_list = [cycle.zfill(cycle_length)]
        elif isinstance(cycle, int):
            assert cycle > 0, "Cycle number must be positive"
            cycle_list = [str(cycle).zfill(cycle_length)]
        elif isinstance(cycle, list):
            cycle_list = []
            for c in cycle:
                assert int(c) > 0, "Cycle number must be positive"
                cycle_list.append(str(c).zfill(cycle_length))
        else:
            raise TypeError("Please enter the cycle number as a list or string")

        # check if user-entered cycle is outside of currently available range
        if not set(all_cycles) & set(cycle_list):
            warnings.filterwarnings("always")
            warnings.warn("Listed cycle is not presently available")

        return cycle_list


def tracks(track):
    """
    Check if the submitted RGT is valid, and warn the user if not available.
    """
    track_length = 4
    # total number of ICESat-2 satellite RGTs is 1387
    all_tracks = [str(tr + 1).zfill(track_length) for tr in range(1387)]

    if track is None:
        return []
    else:
        if isinstance(track, str):
            assert int(track) > 0, "Reference Ground Track must be positive"
            track_list = [track.zfill(track_length)]
        elif isinstance(track, int):
            assert track > 0, "Reference Ground Track must be positive"
            track_list = [str(track).zfill(track_length)]
        elif isinstance(track, list):
            track_list = []
            for t in track:
                assert int(t) > 0, "Reference Ground Track must be positive"
                track_list.append(str(t).zfill(track_length))
        else:
            raise TypeError(
                "Please enter the Reference Ground Track as a list or string"
            )

        # check if user-entered RGT is outside of the valid range
        if not set(all_tracks) & set(track_list):
            warnings.filterwarnings("always")
            warnings.warn("Listed Reference Ground Track is not available")

        return track_list


# DevGoal: clean up; turn into classes (see validate_inputs_classes.py)

def spatial(spatial_extent):
    """
    Validate the input spatial extent and return the needed parameters to the query object.

    spatial_extent : expects one of the following:

        * list of coordinates (stored in a list OR np.ndarray) as one of:
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
            * file must contain more than one polygon
    """

    scalar_types = (int, float, np.int64)

    # Check if spatial_extent is a bounding box or a polygon (list of coords)
    # Check if spatial_extent is a "list" or an "numpy.ndarray"

    # NOTE: I think that the input is assumed to be "strings"; thats why we must cast to float later
    # This may also "flatten" the array so geospatial.geodataframe will work
    if isinstance(spatial_extent, (list, np.ndarray)):

        # bounding box
        if len(spatial_extent) == 4 and all(isinstance(i, scalar_types) for i in spatial_extent):

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
            _spat_extent = [float(x) for x in spatial_extent]

            # we now know extent_type is "bounding_box" so set this accordingly
            extent_type = "bounding_box"

        # user-entered polygon as list of lon, lat coordinate pairs

        # (NOTE: The all() function returns True if all items in an iterable are true, otherwise it returns False.)

        # TODO: Write this "check" as a separate function? maybe do the same with bounding box?
        elif all(type(i) in [list, tuple, np.ndarray] for i in spatial_extent) \
                and all(all(isinstance(i[j], scalar_types) for j in range(len(i))) for i in spatial_extent):

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
            extent_type = "polygon"

            # make all elements of polygon floats
            polygon = [float(i) for i in polygon]

            # create a geodataframe object from polygon
            gdf = geospatial.geodataframe(extent_type, polygon, file=False)
            _spat_extent = gdf.iloc[0].geometry

            # _spat_extent = polygon
            # extent_type = 'polygon'
            # TODO: Check if this DevGoal is still ongoing
            # #DevGoal: properly format this input type (and any polygon type) so that it is clockwise (and only contains 1 pole)!!
            # warnings.warn("this type of input is not yet well handled and you may not be able to find data")

        # user-entered polygon as a single list of lon and lat coordinates
        elif all(isinstance(i, scalar_types) for i in spatial_extent):
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

        else:
            raise ValueError(
                "Your spatial extent does not meet minimum input criteria or the input format is not correct"
            )

        # DevGoal: write a test for this?
        # make sure there is nothing set to _geom_filepath since its existence determines later steps

        try:
            del _geom_filepath
        except:
            UnboundLocalError

    # DevGoal: revisit this section + geospatial.geodataframe.
    # There might be some good ways to combine the functionality in these checks with that

    # Else if spatial_extent is a string (i.e. a (potential) filename)
    elif isinstance(spatial_extent, str):
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

            _spat_extent = gdf.iloc[0].geometry

            # _spat_extent = apifmt._fmt_polygon(spatial_extent)

            _geom_filepath = spatial_extent
        # Filename has an invalid extension type; raise a TypeError
        else:
            raise TypeError("Input spatial extent file must be a kml, shp, or gpkg")

    # DevGoal: currently no specific test for this if statement...
    if "_geom_filepath" not in locals():
        _geom_filepath = None
    #TODO: Check this warning.
    return extent_type, _spat_extent, _geom_filepath


def temporal(date_range, start_time, end_time):
    """
    Validate the input temporal parameters and return the needed parameters to the query object.
    """
    if isinstance(date_range, list):
        if len(date_range) == 2:
            _start = dt.datetime.strptime(date_range[0], "%Y-%m-%d")
            _end = dt.datetime.strptime(date_range[1], "%Y-%m-%d")
            assert _start.date() <= _end.date(), "Your date range is invalid"

        else:
            raise ValueError(
                "Your date range list is the wrong length. It should have start and end dates only."
            )

    # DevGoal: accept more date/time input formats
    #         elif isinstance(date_range, date-time object):
    #             print('it is a date-time object')
    #         elif isinstance(date_range, dict):
    #             print('it is a dictionary. now check the keys for start and end dates')

    if start_time is None:
        _start = _start.combine(
            _start.date(), dt.datetime.strptime("00:00:00", "%H:%M:%S").time()
        )
    else:
        if isinstance(start_time, str):
            _start = _start.combine(
                _start.date(), dt.datetime.strptime(start_time, "%H:%M:%S").time()
            )
        else:
            raise TypeError("Please enter your start time as a string")

    if end_time is None:
        _end = _start.combine(
            _end.date(), dt.datetime.strptime("23:59:59", "%H:%M:%S").time()
        )
    else:
        if isinstance(end_time, str):
            _end = _start.combine(
                _end.date(), dt.datetime.strptime(end_time, "%H:%M:%S").time()
            )
        else:
            raise TypeError("Please enter your end time as a string")

    return _start, _end
