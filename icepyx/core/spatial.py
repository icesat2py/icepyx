from itertools import chain
import os
from typing import Literal, Optional, Union, cast
import warnings

import geopandas as gpd
import harmony
import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

import icepyx.core.exceptions

# DevGoal: need to update the spatial_extent docstring to describe coordinate order for input


ExtentType = Literal["bounding_box", "polygon"]


def _convert_spatial_extent_to_list_of_floats(
    spatial_extent: Union[list[float], list[tuple[float, float]], Polygon],
) -> list[float]:
    # This is already a list of floats
    if isinstance(spatial_extent, list) and isinstance(spatial_extent[0], float):
        spatial_extent = cast(list[float], spatial_extent)
        return spatial_extent
    elif isinstance(spatial_extent, Polygon):
        # Convert `spatial_extent` into a list of floats like:
        # `[longitude1, latitude1, longitude2, latitude2, ...]`
        spatial_extent = [
            float(coord) for point in spatial_extent.exterior.coords for coord in point
        ]
        return spatial_extent
    elif isinstance(spatial_extent, list) and isinstance(spatial_extent[0], tuple):
        # Convert the list of tuples into a flat list of floats
        spatial_extent = cast(list[tuple[float, float]], spatial_extent)
        spatial_extent = list(chain.from_iterable(spatial_extent))
        return spatial_extent
    else:
        raise TypeError(
            "Unrecognized spatial_extent that"
            " cannot be converted into a list of floats:"
            f"{spatial_extent=}"
        )


def _geodataframe_from_bounding_box(
    spatial_extent: list[float],
    xdateline: bool,
) -> gpd.GeoDataFrame:
    if xdateline is True:
        cartesian_lons = [i if i > 0 else i + 360 for i in spatial_extent[0:-1:2]]
        cartesian_spatial_extent = [
            item for pair in zip(cartesian_lons, spatial_extent[1::2]) for item in pair
        ]
        bbox = box(
            cartesian_spatial_extent[0],
            cartesian_spatial_extent[1],
            cartesian_spatial_extent[2],
            cartesian_spatial_extent[3],
        )
    else:
        bbox = box(
            spatial_extent[0],
            spatial_extent[1],
            spatial_extent[2],
            spatial_extent[3],
        )

    # TODO: test case that ensures gdf is constructed as expected (correct coords, order, etc.)
    # HACK: Disabled Pyright due to issue
    #       https://github.com/geopandas/geopandas/issues/3115
    return gpd.GeoDataFrame(geometry=[bbox], crs="epsg:4326")  # pyright: ignore[reportCallIssue]


def _geodataframe_from_polygon_list(
    spatial_extent: list[float],
    xdateline: bool,
) -> gpd.GeoDataFrame:
    if xdateline is True:
        cartesian_lons = [i if i > 0 else i + 360 for i in spatial_extent[0:-1:2]]
        spatial_extent = [
            item for pair in zip(cartesian_lons, spatial_extent[1::2]) for item in pair
        ]

    spatial_extent_geom = Polygon(
        # syntax of dbl colon is- "start:stop:steps"
        # 0::2 = start at 0, grab every other coord after
        # 1::2 = start at 1, grab every other coord after
        zip(spatial_extent[0::2], spatial_extent[1::2])
    )  # spatial_extent
    # TODO: check if the crs param should always just be epsg:4326 for everything OR if it should be a parameter
    # HACK: Disabled Pyright due to issue
    #       https://github.com/geopandas/geopandas/issues/3115
    return gpd.GeoDataFrame(  # pyright: ignore[reportCallIssue]
        index=[0], crs="epsg:4326", geometry=[spatial_extent_geom]
    )


def geodataframe(
    extent_type: ExtentType,
    spatial_extent: Union[str, list[float], list[tuple[float, float]], Polygon],
    file: bool = False,
    xdateline: Optional[bool] = None,
) -> gpd.GeoDataFrame:
    """
    Return a geodataframe of the spatial extent

    Parameters
    ----------
    extent_type :
        One of 'bounding_box' or 'polygon', indicating what type of input the spatial extent is

    spatial_extent :
        A list containing the spatial extent, a shapely.Polygon, a list of
        tuples (i.e.,, `[(longitude1, latitude1), (longitude2, latitude2),
        ...]`)containing floats, OR a string containing a filename.
        If file is False, spatial_extent should be a shapely.Polygon,
        list of bounding box coordinates in decimal degrees of [lower-left-longitude,
        lower-left-latitute, upper-right-longitude, upper-right-latitude] or polygon vertices as
        [longitude1, latitude1, longitude2, latitude2, ...
        longitude_n,latitude_n, longitude1,latitude1].

        If file is True, spatial_extent is a string containing the full file path and filename
        to the file containing the desired spatial extent.

    file :
        Indication for whether the spatial_extent string is a filename or coordinate list

    xdateline :
        Whether the given extent crosses the dateline

    Returns
    -------
    gdf : GeoDataFrame
        Returns a GeoPandas GeoDataFrame containing the spatial extent.
        The GeoDataFrame will have only one entry unless a geospatial file
        was submitted.

    See Also
    --------
    icepyx.Query

    Examples
    --------
    >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
    >>> gdf = geodataframe(reg_a.spatial.extent_type, reg_a.spatial.extent)
    >>> gdf.geometry
    0    POLYGON ((-48 68, -48 71, -55 71, -55 68, -48 ...
    Name: geometry, dtype: geometry
    """
    # DevGoal: the crs setting and management needs to be improved

    # If extent_type is a polygon AND from a file, create a geopandas geodataframe from it
    if file is True:
        if extent_type == "polygon":
            return gpd.read_file(spatial_extent)
        else:
            raise TypeError("When 'file' is True, 'extent_type' must be 'polygon'")

    if isinstance(spatial_extent, str):
        raise TypeError(
            f"Expected list of floats, list of tuples of floats, or Polygon, received {spatial_extent=}"
        )

    #### Non-file processing
    # Most functions that this function calls requires the spatial extent as a
    # list of floats. This function provides that.
    spatial_extent_list = _convert_spatial_extent_to_list_of_floats(
        spatial_extent=spatial_extent,
    )

    if xdateline is None:
        xdateline = check_dateline(
            extent_type,
            spatial_extent_list,
        )

    # DevGoal: Currently this if/else within this elif are not tested...
    if extent_type == "bounding_box":
        return _geodataframe_from_bounding_box(
            spatial_extent=spatial_extent_list,
            xdateline=xdateline,
        )

    elif extent_type == "polygon":
        # if spatial_extent is already a Polygon
        if isinstance(spatial_extent, Polygon):
            spatial_extent_geom = spatial_extent
            return gpd.GeoDataFrame(  # pyright: ignore[reportCallIssue]
                index=[0], crs="epsg:4326", geometry=[spatial_extent_geom]
            )

        # The input must be a list of floats.
        return _geodataframe_from_polygon_list(
            spatial_extent=spatial_extent_list,
            xdateline=xdateline,
        )

    else:
        raise TypeError(
            f"Your spatial extent type ({extent_type}) is not an accepted "
            "input and a geodataframe cannot be constructed"
        )


def check_dateline(
    extent_type: ExtentType,
    # TODO: I think this is actually wrong. It expects a different type of
    # spatial_extent depending on the `extent_type`, showing below.
    spatial_extent: list[float],
) -> bool:
    """
    Check if a bounding box or polygon input cross the dateline.

    Parameters
    ----------
    extent_type :
        One of 'bounding_box' or 'polygon', indicating what type of input the spatial extent is

    spatial_extent :
        A list containing the spatial extent as
        coordinates in decimal degrees of
        [longitude1, latitude1, longitude2, latitude2, ... longitude_n,latitude_n, longitude1,latitude1].


    Returns
    -------
    boolean
        indicating whether or not the spatial extent crosses the dateline.
    """
    if extent_type == "bounding_box":
        # We expect the bounding_box to be a list of floats.
        if spatial_extent[0] > spatial_extent[2]:
            # if lower left lon is larger then upper right lon, verify the values are crossing the dateline
            assert spatial_extent[0] - 360 <= spatial_extent[2]

            warnings.warn(
                "Your bounding box was identified as crossing the dateline."
                "If this is not correct, please add `xdateline=False` to your `ipx.Query`"
            )
            return True

        else:
            return False

    # this works properly, but limits the user to at most 270 deg longitude...
    elif extent_type == "polygon":
        # This checks that the first instance of `spatial_extent` NOT a list or
        # a tuple. Assumes that this is a list of floats.
        assert not isinstance(
            spatial_extent[0], (list, tuple)
        ), "Your polygon list is the wrong format for this function."
        lonlist = spatial_extent[0:-1:2]
        if np.any(
            [abs(lonlist[i] - lonlist[i + 1]) > 270 for i in range(len(lonlist) - 1)]
        ):
            warnings.warn(
                "Your polygon was identified as crossing the dateline."
                "If this is not correct, please add `xdateline=False` to your `ipx.Query`"
            )
            return True
        else:
            return False


def validate_bounding_box(
    spatial_extent: Union[list[float], NDArray[np.floating]],
) -> tuple[Literal["bounding_box"], list[float], None]:
    """
    Validates the spatial_extent parameter as a bounding box.

    If the spatial_extent is a valid bounding box, returns a tuple containing the Spatial object parameters
    for the bounding box; otherwise, throw an error containing the reason the bounding box is invalid.

    Parameters
    ----------
    spatial_extent:
        A list or np.ndarray of exactly 4 numerics representing bounding box coordinates
        in decimal degrees.

        Must be provided in the order:
        [lower-left-longitude, lower-left-latitude,
        upper-right-longitude, upper-right-latitude])
    """

    # Latitude must be between -90 and 90 (inclusive); check for this here
    assert (
        -90 <= spatial_extent[1] <= 90
    ), "Invalid latitude value (must be between -90 and 90, inclusive)"
    assert (
        -90 <= spatial_extent[3] <= 90
    ), "Invalid latitude value (must be between -90 and 90, inclusive)"

    assert (
        -180 <= spatial_extent[0] <= 180
    ), "Invalid longitude value (must be between -180 and 180, inclusive)"
    assert (
        -180 <= spatial_extent[2] <= 180
    ), "Invalid longitude value (must be between -180 and 180, inclusive)"

    # If the lower left latitude is greater than the upper right latitude, throw an error
    assert spatial_extent[1] <= spatial_extent[3], "Invalid bounding box latitudes"

    spatial_extent = [float(x) for x in spatial_extent]

    return "bounding_box", spatial_extent, None


def validate_polygon_pairs(
    spatial_extent: Union[list[tuple[float, float]], NDArray[np.void]],
) -> tuple[Literal["polygon"], list[float], None]:
    """
    Validates the spatial_extent parameter as a polygon from coordinate pairs.

    If the spatial_extent is a valid polygon, returns a tuple containing the Spatial object parameters
    for the polygon;

    otherwise, throw an error containing the reason the polygon is invalid.

    Parameters
    ----------
    spatial_extent:

        A list or np.ndarray of tuples representing polygon coordinate pairs in decimal
        degrees in the order:

            [
                (longitude_1, latitude_1),
                ...,
                (longitude_n, latitude_n),
                (longitude_1,latitude_1),
            ]

        If the first and last coordinate pairs are NOT equal,
        the polygon will be closed automatically (last point will be connected to the
        first point).
    """
    # Check to make sure all elements of spatial_extent are coordinate pairs; if not, raise an error
    if any(len(i) != 2 for i in spatial_extent):
        raise ValueError(
            "Each element in spatial_extent should be a list or tuple of length 2"
        )

    # If there are less than 4 vertices, raise an error
    assert len(spatial_extent) >= 4, "Your spatial extent polygon has too few vertices"

    if (spatial_extent[0][0] != spatial_extent[-1][0]) or (
        spatial_extent[0][1] != spatial_extent[-1][1]
    ):
        # Throw a warning
        warnings.warn(
            "WARNING: Polygon's first and last point's coordinates differ,"
            " closing the polygon automatically."
        )
        # Add starting long/lat to end
        if isinstance(spatial_extent, list):
            # use list.append() method
            spatial_extent.append(spatial_extent[0])

        elif isinstance(spatial_extent, np.ndarray):
            # use np.insert() method
            spatial_extent = np.insert(
                spatial_extent, len(spatial_extent), spatial_extent[0]
            )

    polygon = (",".join([str(c) for xy in spatial_extent for c in xy])).split(",")

    # make all elements of polygon floats
    polygon = [float(i) for i in polygon]

    return "polygon", polygon, None


def validate_polygon_list(
    spatial_extent: Union[
        list[float],
        NDArray[np.floating],
    ],
) -> tuple[Literal["polygon"], list[float], None]:
    """
    Validates the spatial_extent parameter as a polygon from a list of coordinates.

    If the spatial_extent is a valid polygon, returns a tuple containing the Spatial object parameters
    for the polygon;

    otherwise, throw an error containing the reason the polygon is invalid.

    Parameters
    ----------
    spatial_extent:
        A list or np.ndarray of numerics representing polygon coordinates,
        provided as coordinate pairs in decimal degrees in the order:
        [longitude1, latitude1, longitude2, latitude2, ...
        ... longitude_n,latitude_n, longitude1,latitude1]

        If the first and last coordinate pairs are NOT equal,
        the polygon will be closed automatically (last point will be connected to the first point).
    """

    # user-entered polygon as a single list of lon and lat coordinates
    assert len(spatial_extent) >= 8, "Your spatial extent polygon has too few vertices"
    assert (
        len(spatial_extent) % 2 == 0
    ), "Your spatial extent polygon list should have an even number of entries"

    if (spatial_extent[0] != spatial_extent[-2]) or (
        spatial_extent[1] != spatial_extent[-1]
    ):
        warnings.warn(
            "WARNING: Polygon's first and last point's coordinates differ,"
            " closing the polygon automatically."
        )

        # Add starting long/lat to end
        if isinstance(spatial_extent, list):
            spatial_extent.append(spatial_extent[0])
            spatial_extent.append(spatial_extent[1])

        elif isinstance(spatial_extent, np.ndarray):
            spatial_extent = np.insert(
                spatial_extent, len(spatial_extent), spatial_extent[0]
            )
            spatial_extent = np.insert(
                spatial_extent, len(spatial_extent), spatial_extent[1]
            )

    polygon = [float(i) for i in spatial_extent]

    return "polygon", polygon, None


def validate_polygon_file(
    spatial_extent: str,
) -> tuple[Literal["polygon"], gpd.GeoDataFrame, str]:
    """
    Validates the spatial_extent parameter as a polygon from a file.

    If the spatial_extent parameter contains a valid polygon,
    returns a tuple containing the Spatial object parameters for the polygon;

    otherwise, throw an error containing the reason the polygon/polygon file is invalid.

    Parameters
    ----------
    spatial_extent: string
                     A string representing a geospatial polygon file (kml, shp, gpkg)
                     * must provide full file path
                     * recommended for file to only contain 1 polygon.
                         * if multiple polygons, only the first polygon is selected at this time.

    """

    # Check if the filename path exists; if not, throw an error
    # print("print statements work \n")
    # print("SPATIAL EXTENT: " + spatial_extent + "\n")
    assert os.path.exists(
        spatial_extent
    ), "Check that the path and filename of your geometry file are correct"

    # DevGoal: more robust polygon inputting (see Bruce's code):
    # correct for clockwise/counterclockwise coordinates, deal with simplification, etc.

    if spatial_extent.split(".")[-1] in ["kml", "shp", "gpkg"]:
        extent_type = "polygon"
        gdf = geodataframe(extent_type, spatial_extent, file=True)

        return "polygon", gdf, spatial_extent

    else:
        raise TypeError("Input spatial extent file must be a kml, shp, or gpkg")


class Spatial:
    _ext_type: ExtentType
    _geom_file: Optional[str]
    _spatial_ext: list[float]

    def __init__(
        self,
        spatial_extent: Union[
            str,  # Filepath
            list[float],  # Bounding box or polygon
            list[tuple[float, float]],  # Polygon
            NDArray,  # Polygon
            None,
        ],
        **kwarg,
    ):
        """
        Validates input from "spatial_extent" argument, then creates a Spatial object with validated inputs
        as properties of the object.

        Spatial objects are to be used by icepyx.Query to store validated geospatial information required by the Query.

        Parameters
        ----------
        spatial_extent : list or string
            * list of coordinates
             (stored in a list of numerics, list of tuples, OR np.ndarray) as one of:
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

        xdateline : boolean, default None
            Optional keyword argument to let user specify whether the spatial input crosses the dateline or not.


        See Also
        --------
        icepyx.Query


        Examples
        --------
        Initializing Spatial with a bounding box.

        >>> reg_a_bbox = [-55, 68, -48, 71]
        >>> reg_a = Spatial(reg_a_bbox)
        >>> print(reg_a)
        Extent type: bounding_box
        Coordinates: [-55.0, 68.0, -48.0, 71.0]

        Initializing Query with a list of polygon vertex coordinate pairs.

        >>> reg_a_poly = [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
        >>> reg_a = Spatial(reg_a_poly)
        >>> print(reg_a)
        Extent type: polygon
        Coordinates: [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]

        Initializing Query with a geospatial polygon file.

        >>> from pathlib import Path
        >>> aoi = Path('./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg').resolve()
        >>> reg_a = Spatial(str(aoi))
        >>> print(reg_a) # doctest: +SKIP
        Extent Type: polygon
        Source file: ./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg
        Coordinates: [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]
        """

        scalar_types = (int, float, np.int64)

        # Check if spatial_extent is a list of coordinates (bounding box or polygon)
        if isinstance(spatial_extent, (list, np.ndarray)):
            # bounding box
            if len(spatial_extent) == 4 and all(
                isinstance(i, scalar_types)  # pyright: ignore[reportArgumentType]
                for i in spatial_extent
            ):
                (
                    self._ext_type,
                    self._spatial_ext,
                    self._geom_file,
                ) = validate_bounding_box(
                    # HACK: Unfortunately, the typechecker can't narrow based on the
                    # above conditional expressions. Tell the typechecker, "trust us"!
                    cast(
                        Union[list[float], NDArray[np.floating]],
                        spatial_extent,
                    ),
                )

            # polygon (as list of lon, lat coordinate pairs, in tuples)
            elif all(
                type(i) in [list, tuple, np.ndarray] for i in spatial_extent
            ) and all(
                all(isinstance(i[j], scalar_types) for j in range(len(i)))  # pyright: ignore[reportArgumentType,reportIndexIssue]
                for i in spatial_extent
            ):
                (
                    self._ext_type,
                    self._spatial_ext,
                    self._geom_file,
                ) = validate_polygon_pairs(
                    # HACK: Unfortunately, the typechecker can't narrow based on the
                    # above conditional expressions. Tell the typechecker, "trust us"!
                    cast(
                        Union[list[tuple[float, float]], NDArray[np.void]],
                        spatial_extent,
                    )
                )

            # polygon (as list of lon, lat coordinate pairs, single "flat" list)
            elif all(isinstance(i, scalar_types) for i in spatial_extent):  # pyright: ignore[reportArgumentType]
                (
                    self._ext_type,
                    self._spatial_ext,
                    self._geom_file,
                ) = validate_polygon_list(
                    # HACK: Unfortunately, the typechecker can't narrow based on the
                    # above conditional expressions. Tell the typechecker, "trust us"!
                    cast(
                        Union[list[float], NDArray[np.floating]],
                        spatial_extent,
                    )
                )
            else:
                # TODO: Change this warning to be like "usage", tell user possible accepted input types
                raise ValueError(
                    "Your spatial extent does not meet minimum input criteria or the input format is not correct"
                )

        # Check if spatial_extent is a string (i.e. a (potential) filename)
        elif isinstance(spatial_extent, str):
            self._ext_type, self._gdf_spat, self._geom_file = validate_polygon_file(
                spatial_extent
            )

            # TODO: assess if it's necessary to have a value for _spatial_extent if the input is a file (since it can be plotted from the gdf)
            extpoly = self._gdf_spat.geometry.unary_union.boundary

            try:
                arrpoly = (
                    ",".join([str(c) for xy in zip(*extpoly.coords.xy) for c in xy])
                ).split(",")
            except NotImplementedError:
                arrpoly = (
                    ",".join(
                        [
                            str(c)
                            for xy in zip(*extpoly.envelope.boundary.coords.xy)
                            for c in xy
                        ]
                    )
                ).split(",")

            self._spatial_ext = [float(i) for i in arrpoly]

        # check for cross dateline keyword submission
        if "xdateline" in kwarg:
            self._xdateln = kwarg["xdateline"]
            assert self._xdateln in [
                True,
                False,
            ], "Your 'xdateline' value is invalid. It must be boolean."

    def __str__(self) -> str:
        if self._geom_file is not None:
            return "Extent type: {0}\nSource file: {1}\nCoordinates: {2}".format(
                self._ext_type, self._geom_file, self._spatial_ext
            )
        else:
            return "Extent type: {0}\nCoordinates: {1}".format(
                self._ext_type, self._spatial_ext
            )

    @property
    def extent(self) -> list[float]:
        """
        Return the coordinates of the spatial extent of the Spatial object.

        The result will be returned as an array.
        For input geometry files with multiple features, the boundary of the
        the unary union of all features is returned.

        Returns
        -------
        spatial extent : array
            An array of bounding coordinates.
        """

        return self._spatial_ext

    @property
    def extent_as_gdf(self) -> gpd.GeoDataFrame:
        """
        Return the spatial extent of the query object as a GeoPandas GeoDataframe.

        Returns
        -------
        extent_gdf : GeoDataframe
            A GeoDataframe containing the spatial region of interest.
        """

        # TODO: test this
        xdateln = self._xdateln if hasattr(self, "_xdateln") else None

        if not hasattr(self, "_gdf_spat"):
            if self._geom_file is not None:
                self._gdf_spat = geodataframe(
                    self._ext_type, self._spatial_ext, file=True, xdateline=xdateln
                )
            else:
                self._gdf_spat = geodataframe(
                    self._ext_type, self._spatial_ext, xdateline=xdateln
                )

        return self._gdf_spat

    @property
    def extent_type(self) -> ExtentType:
        """
        Return the extent type of the Spatial object as a string.

        Examples
        --------
        >>> reg_a = Spatial([-55, 68, -48, 71])
        >>> reg_a.extent_type
        'bounding_box'

        >>> reg_a = Spatial([(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)])
        >>> reg_a.extent_type
        'polygon'
        """

        return self._ext_type

    @property
    def extent_file(self) -> Optional[str]:
        """
        Return the path to the geospatial polygon file containing the Spatial object's spatial extent.
        If the spatial extent did not come from a file (i.e. user entered list of coordinates), this will return None.

        Examples
        --------
        >>> reg_a = Spatial([-55, 68, -48, 71])
        >>> reg_a.extent_file


        >>> from pathlib import Path
        >>> reg_a = Spatial(str(Path('./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg').resolve()))
        >>> reg_a.extent_file # doctest: +SKIP
        ./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg
        """
        return self._geom_file

    # ----------------------------------------------------------------------
    # Methods

    # TODO: can use this docstring as a todo list
    def fmt_for_CMR(self) -> str:
        """
        Format the spatial extent for NASA's Common Metadata Repository (CMR) API.

        CMR spatial inputs must be formatted a specific way.
        This method formats the given spatial extent to be a valid submission.
        For large/complex polygons, this includes simplifying the polygon (NOTE: currently not all polygons are simplified enough).
        Coordinates will be properly ordered, and the required string formatting applied.
        For small regions, a buffer may be added.

        Returns
        -------
        string
            Properly formatted string of spatial data for submission to CMR API.


        """
        # CMR keywords: ['bounding_box', 'polygon']
        if self.extent_type == "bounding_box":
            return ",".join(map(str, self._spatial_ext))

        elif self.extent_type == "polygon":
            poly = self.extent_as_gdf.geometry

            if any(
                geomtype in ["MultiPoint", "MultiLineString", "MultiPolygon"]
                for geomtype in poly.geom_type
            ):
                poly = poly.convex_hull

            poly = poly.unary_union

            # Simplify polygon. The larger the tolerance value, the more simplified the polygon. See Bruce Wallin's function to do this
            poly = poly.simplify(0.05, preserve_topology=True)
            poly = orient(poly, sign=1.0)

            # Format dictionary to polygon coordinate pairs for API submission
            polygon = (
                ",".join([str(c) for xy in zip(*poly.exterior.coords.xy) for c in xy])
            ).split(",")
            extent = [float(i) for i in polygon]

            # TODO: explore how this will be impacted if the polygon is read in from a shapefile and crosses the dateline
            if hasattr(self, "_xdateln") and self._xdateln is True:
                neg_lons = [i if i < 181.0 else i - 360 for i in extent[0:-1:2]]
                extent = [item for pair in zip(neg_lons, extent[1::2]) for item in pair]

            return ",".join(map(str, extent))

        else:
            raise icepyx.core.exceptions.ExhaustiveTypeGuardException

    def fmt_for_EGI(self) -> str:
        """
        Format the spatial extent input into a subsetting key value for submission to EGI (the NSIDC DAAC API).

        EGI spatial inputs must be formatted a specific way.
        This method formats the given spatial extent to be a valid submission.
        DevGoal: For large/complex polygons, this includes simplifying the polygon.
        Coordinates will be properly ordered, and the required string formatting applied.

        Returns
        -------
        string
            Properly formatted json string for submission to EGI (NSIDC API).
        """

        # subsetting keywords: ['bbox','Boundingshape'] - these are set in APIformatting
        if self.extent_type == "bounding_box":
            return ",".join(map(str, self._spatial_ext))

        # TODO: add handling for polygons that cross the dateline
        elif self.extent_type == "polygon":
            poly = self.extent_as_gdf.geometry[0]
            poly = orient(poly, sign=1.0)
            egi_extent = gpd.GeoSeries(poly).to_json()
            return egi_extent.replace(" ", "")  # remove spaces for API call

        else:
            raise icepyx.core.exceptions.ExhaustiveTypeGuardException

    def fmt_for_harmony(self) -> dict[str, harmony.BBox]:
        """
        Format the spatial extent input into format expected by `harmony-py`.

        Returns a dictionary with keys mapping to `harmony.Request` kwargs, with
        values appropriately formated for the harmony request.

        `harmony-py` can take two different spatial parameters:

        * `spatial`: "Bounding box spatial constraints on the data or Well Known
          Text (WKT) string describing the spatial constraints." The "Bounding
          box" is expected to be a `harmony.BBox`.
        * `shape`: "a file path to an ESRI Shapefile zip, GeoJSON file, or KML
          file to use for spatial subsetting. Note: not all collections support
          shapefile subsetting"

        Question: is `spatial` the same as `shape`, in terms of performance? If
        so, we could be consistent and always turn the input into geojson and
        pass that along to harmony. Otherwise we should choose `spatial` if the
        extent_type is bounding, otherwise `shape`.
        Answer: No! They're not the same. They map to different harmony
        parameters and each is a different service. E.g., some collections may
        have bounding box subsetting while others have shape subsetting (or
        both).
        TODO: think more about how we verify if certain inputs are valid for
        harmony. E.g., do we need to check the capabilities of each and
        cross-check that with user inputs to determine which action to take?
        Also: Does `icepyx` always perform subsetting based on user input? If
        not, how do we determine which parameters are for finding granules vs
        performing subetting?

        Question: is there any way to pass in a geojson string directly, so that
        we do not have to mock out a file just for harmony?  Answer: no, not
        direcly. `harmony-py` wants a path to a file on disk. We may want to
        have the function that submits the request to harmony with `harmony-py`
        accept something that's easily-serializable to a geojson file so that it
        can manage the lifespan of the file. It would be best (I think) to avoid
        writing tmp files to disk in this function, because it doesn't know when
        the request gets made/when to cleanup the file. That means that we may
        leave stray files on the user's computer. Ideally, we would be able to
        pass `harmony-py` a bytes object (or a shapely Polygon!)
        """
        # Begin with bounding box because this is the simplest case.
        if self.extent_type == "bounding_box":
            harmony_kwargs = {
                "bbox": harmony.BBox(
                    w=self.extent[0],
                    s=self.extent[1],
                    e=self.extent[2],
                    n=self.extent[3],
                )
            }

            return harmony_kwargs
        else:
            raise NotImplementedError
