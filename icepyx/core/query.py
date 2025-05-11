from functools import cached_property
import json
import logging
from pathlib import Path
from pprint import pprint
import sys
import time
from typing import Any, Dict, Union

from deprecated import deprecated
import earthaccess
import geopandas as gpd
import harmony
import matplotlib.pyplot as plt

import icepyx.core.APIformatting as apifmt
from icepyx.core.auth import EarthdataAuthMixin
from icepyx.core.granules import Granules, gran_IDs
from icepyx.core.harmony import HarmonyApi, HarmonyTemporal
import icepyx.core.is2ref as is2ref
from icepyx.core.orders import DataOrder
import icepyx.core.spatial as spat
import icepyx.core.temporal as tp
from icepyx.core.types import CMRParams
import icepyx.core.validate_inputs as val
from icepyx.core.variables import Variables
from icepyx.core.visualization import Visualize


class GenQuery:
    """
    Base class for querying data.

    Generic components of query object that specifically handles
    spatio-temporal constraints applicable to all datasets.
    Extended by Query (ICESat-2) and Quest (other products).

    Parameters
    ----------
    spatial_extent : list of coordinates or string (i.e. file name)
        Spatial extent of interest, provided as a bounding box,
        list of polygon coordinates, or
        geospatial polygon file.
        NOTE: Longitude values are assumed to be in the range -180 to +180,
        with 0 being the Prime Meridian (Greenwich).
        See xdateline for regions crossing the date line.
        You can submit at most one bounding box or list of polygon coordinates.
        Per NSIDC requirements, geospatial polygon files may only contain one feature (polygon).
        Bounding box coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute,
        upper-right-longitude, upper-right-latitude].
        Polygon coordinates should be provided as coordinate pairs in decimal degrees as
        [(longitude1, latitude1), (longitude2, latitude2), ... (longitude_n,latitude_n), (longitude1,latitude1)]
        or
        [longitude1, latitude1, longitude2, latitude2, ... longitude_n,latitude_n, longitude1,latitude1].
        Your list must contain at least four points, where the first and last are identical.
        Geospatial polygon files are entered as strings with the full file path and
        must contain only one polygon with the area of interest.
        Currently supported formats are: kml, shp, and gpkg
    date_range : list or dict, as follows
        Date range of interest, provided as start and end dates, inclusive.
        Accepted input date formats are:
            * YYYY-MM-DD string
            * YYYY-DOY string
            * datetime.date object (if times are included)
            * datetime.datetime objects (if no times are included)
        where YYYY = 4 digit year, MM = 2 digit month, DD = 2 digit day, DOY = 3 digit day of year.
        Date inputs are accepted as a list or dictionary with `start_date` and `end_date` keys.
        Currently, a list of specific dates (rather than a range) is not accepted.
        TODO: allow searches with a list of dates, rather than a range.
    start_time : str, datetime.time, default None
        Start time in UTC/Zulu (24 hour clock).
        Input types are  an HH:mm:ss string or datetime.time object
        where HH = hours, mm = minutes, ss = seconds.
        If None is given (and a datetime.datetime object is not supplied for `date_range`),
        a default of 00:00:00 is applied.
    end_time : str, datetime.time, default None
        End time in UTC/Zulu (24 hour clock).
        Input types are  an HH:mm:ss string or datetime.time object
        where HH = hours, mm = minutes, ss = seconds.
        If None is given (and a datetime.datetime object is not supplied for `date_range`),
        a default of 23:59:59 is applied.
        If a datetime.datetime object was created without times,
        the datetime package defaults will apply over those of icepyx
    xdateline : bool, default None
        Keyword argument to enforce spatial inputs that cross the International Date Line.
        Internally, this will translate your longitudes to 0 to 360 to construct the
        correct, valid Shapely geometry.

        WARNING: This will allow your request to be properly submitted and visualized.
        However, this flag WILL NOT automatically correct for incorrectly ordered spatial inputs.

    Examples
    --------
    Initializing Query with a bounding box

    >>> reg_a_bbox = [-55, 68, -48, 71]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = GenQuery(reg_a_bbox, reg_a_dates)
    >>> print(reg_a)
    Extent type: bounding_box
    Coordinates: [-55.0, 68.0, -48.0, 71.0]
    Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)

    Initializing Query with a list of polygon vertex coordinate pairs.

    >>> reg_a_poly = [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = GenQuery(reg_a_poly, reg_a_dates)
    >>> print(reg_a)
    Extent type: polygon
    Coordinates: [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]
    Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)

    Initializing Query with a geospatial polygon file.

    >>> from pathlib import Path
    >>> aoi = Path('./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg').resolve()
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> reg_a = GenQuery(str(aoi), reg_a_dates)
    >>> print(reg_a)
    Extent type: polygon
    Coordinates: [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]
    Date range: (2019-02-22 00:00:00, 2019-02-28 23:59:59)

    See Also
    --------
    Query
    Quest
    """

    _temporal: tp.Temporal

    def __init__(
        self,
        spatial_extent=None,
        date_range=None,
        start_time=None,
        end_time=None,
        **kwargs,
    ):
        # validate & init spatial extent
        if "xdateline" in kwargs:
            self._spatial = spat.Spatial(spatial_extent, xdateline=kwargs["xdateline"])
        else:
            self._spatial = spat.Spatial(spatial_extent)

        # valiidate and init temporal constraints
        if date_range:
            self._temporal = tp.Temporal(date_range, start_time, end_time)

    def __str__(self):
        str = "Extent type: {0} \nCoordinates: {1}\nDate range: ({2}, {3})".format(
            self._spatial._ext_type,
            self._spatial._spatial_ext,
            self._temporal._start,
            self._temporal._end,
        )
        return str

    # ----------------------------------------------------------------------
    # Properties

    @property
    def temporal(self) -> Union[tp.Temporal, list[str]]:
        """
        Return the Temporal object containing date/time range information for the query object.

        See Also
        --------
        temporal.Temporal.start
        temporal.Temporal.end
        temporal.Temporal

        Examples
        --------
        >>> reg_a = GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> print(reg_a.temporal)
        Start date and time: 2019-02-20 00:00:00
        End date and time: 2019-02-28 23:59:59

        >>> reg_a = GenQuery([-55, 68, -48, 71],cycles=['03','04','05','06','07'], tracks=['0849','0902'])
        >>> print(reg_a.temporal)
        ['No temporal parameters set']
        """

        if hasattr(self, "_temporal") and self._temporal is not None:
            return self._temporal
        else:
            return ["No temporal parameters set"]

    @property
    def spatial(self):
        """
        Return the spatial object, which provides the underlying functionality for validating
        and formatting geospatial objects. The spatial object has several properties to enable
        user access to the stored spatial extent in multiple formats.

        See Also
        --------
        spatial.Spatial.spatial_extent
        spatial.Spatial.extent_type
        spatial.Spatial.extent_file
        spatial.Spatial

        Examples
        --------
        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.spatial # doctest: +SKIP
        <icepyx.core.spatial.Spatial at [location]>

        >>> print(reg_a.spatial)
        Extent type: bounding_box
        Coordinates: [-55.0, 68.0, -48.0, 71.0]

        """
        return self._spatial

    @property
    def spatial_extent(self):
        """
        Return an array showing the spatial extent of the query object.
        Spatial extent is returned as an input type (which depends on how
        you initially entered your spatial data) followed by the geometry data.
        Bounding box data is [lower-left-longitude, lower-left-latitute,
                            ... upper-right-longitude, upper-right-latitude].
        Polygon data is [longitude1, latitude1, longitude2, latitude2,
                        ... longitude_n,latitude_n, longitude1,latitude1].

        Returns
        -------
        tuple of length 2
        First tuple element is the spatial type ("bounding box" or "polygon").
        Second tuple element is the spatial extent as a list of coordinates.

        Examples
        --------

        # Note: coordinates returned as float, not int
        >>> reg_a = GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.spatial_extent
        ('bounding_box', [-55.0, 68.0, -48.0, 71.0])

        >>> reg_a = GenQuery([(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)],['2019-02-20','2019-02-28'])
        >>> reg_a.spatial_extent
        ('polygon', [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0])

        # NOTE Is this where we wanted to put the file-based test/example?
        # The test file path is: examples/supporting_files/simple_test_poly.gpkg

        See Also
        --------
        Spatial.extent
        Spatial.extent_type
        Spatial.extent_as_gdf

        """

        return (self._spatial._ext_type, self._spatial._spatial_ext)

    @property
    def dates(self) -> list[str]:
        """
        Return an array showing the date range of the query object.
        Dates are returned as an array containing the start and end datetime
        objects, inclusive, in that order.

        Examples
        --------
        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.dates
        ['2019-02-20', '2019-02-28']

        >>> reg_a = GenQuery([-55, 68, -48, 71])
        >>> reg_a.dates
        ['No temporal parameters set']
        """
        if not hasattr(self, "_temporal") or self._temporal is None:
            return ["No temporal parameters set"]
        else:
            return [
                self._temporal._start.strftime("%Y-%m-%d"),
                self._temporal._end.strftime("%Y-%m-%d"),
            ]  # could also use self._start.date()

    @property
    def start_time(self) -> Union[list[str], str]:
        """
        Return the start time specified for the start date.

        Examples
        --------
        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.start_time
        '00:00:00'

        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'], start_time='12:30:30')
        >>> reg_a.start_time
        '12:30:30'

        >>> reg_a = GenQuery([-55, 68, -48, 71])
        >>> reg_a.start_time
        ['No temporal parameters set']
        """
        if not hasattr(self, "_temporal") or self._temporal is None:
            return ["No temporal parameters set"]
        else:
            return self._temporal._start.strftime("%H:%M:%S")

    @property
    def end_time(self) -> Union[list[str], str]:
        """
        Return the end time specified for the end date.

        Examples
        --------
        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.end_time
        '23:59:59'

        >>> reg_a = ipx.GenQuery([-55, 68, -48, 71],['2019-02-20','2019-02-28'], end_time='10:20:20')
        >>> reg_a.end_time
        '10:20:20'

        >>> reg_a = GenQuery([-55, 68, -48, 71])
        >>> reg_a.end_time
        ['No temporal parameters set']
        """
        if not hasattr(self, "_temporal") or self._temporal is None:
            return ["No temporal parameters set"]
        else:
            return self._temporal._end.strftime("%H:%M:%S")


class Query(GenQuery, EarthdataAuthMixin):
    """
    Query and get ICESat-2 data

    ICESat-2 Data object to query, obtain, and perform basic operations on
    available ICESat-2 data products using temporal and spatial input parameters.
    Allows the easy input and formatting of search parameters to match the
    NASA NSIDC DAAC and (development goal-not yet implemented) conversion to multiple data types.
    Expands the superclass GenQuery.

    See the doc page for GenQuery for details on temporal and spatial input parameters.

    Parameters
    ----------
    product : str
        ICESat-2 data product ID, also known as "short name" (e.g. ATL03).
        Available data products can be found at: https://nsidc.org/data/icesat-2/data-sets
    version : str, default most recent version
        Product version, given as a 3 digit string.
        If no version is given, the current version is used. Example: "006"
    cycles : str or list[str], default all available orbital cycles
        Product cycle, given as a 2 digit string, or a list of 2-digit strings.
        If no cycle is given, all available cycles are used. Example: "04"
    tracks : str or list[str], default all available reference ground tracks (RGTs)
        Product track, given as a 4 digit string, or a list of 4-digit strings.
        If no track is given, all available reference ground tracks are used.
        Example: "0594"
    auth : earthaccess.auth.Auth, default None
        An earthaccess authentication object. Available as an argument so an existing
        earthaccess.auth.Auth object can be used for authentication. If not given, a new auth
        object will be created whenever authentication is needed.

    Returns
    -------
    query object

    Examples
    --------
    Initializing Query with a bounding box.

    >>> reg_a_bbox = [-55, 68, -48, 71]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = Query('ATL06', reg_a_bbox, reg_a_dates)
    >>> print(reg_a)
    Product ATL06 v006
    ('bounding_box', [-55.0, 68.0, -48.0, 71.0])
    Date range ['2019-02-20', '2019-02-28']

    Initializing Query with a list of polygon vertex coordinate pairs.

    >>> reg_a_poly = [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = Query('ATL06', reg_a_poly, reg_a_dates)
    >>> reg_a.spatial_extent
    ('polygon', [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0])

    Initializing Query with a geospatial polygon file.

    >>> from pathlib import Path
    >>> aoi = Path('./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg').resolve()
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> reg_a = Query('ATL06', str(aoi), reg_a_dates)
    >>> print(reg_a)
    Product ATL06 v006
    ('polygon', [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0])
    Date range ['2019-02-22', '2019-02-28']

    See Also
    --------
    GenQuery
    """

    _temporal: Union[tp.Temporal, None]
    _CMRparams: apifmt.CMRParameters
    REQUEST_RETRY_INTERVAL_SECONDS = 3

    # ----------------------------------------------------------------------
    # Constructors

    def __init__(
        self,
        product=None,
        spatial_extent=None,
        date_range=None,
        start_time=None,
        end_time=None,
        version=None,
        cycles=None,
        tracks=None,
        auth=None,
        **kwargs,
    ):
        self._prod = is2ref._validate_product(product)

        super().__init__(spatial_extent, date_range, start_time, end_time, **kwargs)

        self._version = val.prod_version(is2ref.latest_version(self._prod), version)
        self._cycles = cycles
        self._tracks = tracks

        # initialize authentication properties
        EarthdataAuthMixin.__init__(self)

        if not hasattr(self, "_temporal"):
            self._temporal = None  # type: ignore[reportIncompatibleVariableOverride]
        if cycles or tracks:
            # get lists of available ICESat-2 cycles and tracks
            # create list of CMR parameters for granule name
            self._readable_granule_name = apifmt._fmt_readable_granules(
                self._prod, cycles=self.cycles, tracks=self.tracks
            )

        logging.basicConfig(level=logging.WARNING)

    # ----------------------------------------------------------------------
    # Properties

    @property
    @deprecated(
        version="1.4.0", reason="order_vars() is going away, use variables() instead"
    )
    def order_vars(self) -> Union[Variables, None]:
        """This used to print the list of vasriables for subsetting, Harmony doesn't provide that for IS2 datasets.
        we do need to implement a class that gets the variables even if it'sm only for listing.
        """
        logging.warning(
            "Deprecated: order_vars() is going away, use variables() instead"
        )
        if self.product:
            self._variables = Variables(product=self.product)  # type: ignore[no-any-return]
            return self._variables
        return None

    @property
    def variables(self) -> Variables:
        if not hasattr(self, "_variables"):
            self._variables = Variables(product=self.product)
        return self._variables

    def show_custom_options(self) -> Dict[str, Any]:
        """
        Display customization/subsetting options available for this product.

        """
        capabilities: dict = {}
        if not hasattr(self, "harmony_api"):
            self.harmony_api = HarmonyApi()
        if self.concept_id:
            capabilities = self.harmony_api.get_capabilities(concept_id=self.concept_id)
            print(json.dumps(capabilities, indent=2))
        return capabilities

    @property
    def CMRparams(self) -> CMRParams:
        """
        Display the CMR key:value pairs that will be submitted.
        It generates the dictionary if it does not already exist.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.CMRparams
        {'temporal': '2019-02-20T00:00:00Z,2019-02-28T23:59:59Z',
        'bounding_box': '-55.0,68.0,-48.0,71.0'}
        """

        if not hasattr(self, "_CMRparams"):
            self._CMRparams = apifmt.Parameters("CMR")

        # dictionary of optional CMR parameters
        kwargs = {}
        kwargs["concept_id"] = self._get_concept_id(self.product, None)

        # temporal CMR parameters
        if hasattr(self, "_temporal") and self.product != "ATL11" and self._temporal:
            kwargs["start"] = self._temporal._start
            kwargs["end"] = self._temporal._end
        # granule name CMR parameters (orbital or file name)
        # DevGoal: add to file name search to optional queries
        if hasattr(self, "_readable_granule_name"):
            kwargs["options[readable_granule_name][pattern]"] = "true"
            kwargs["options[spatial][or]"] = "true"
            kwargs["readable_granule_name[]"] = self._readable_granule_name

        if self._CMRparams.fmted_keys == {}:
            self._CMRparams.build_params(
                extent_type=self._spatial._ext_type,
                spatial_extent=self._spatial.fmt_for_CMR(),
                **kwargs,
            )

        return self._CMRparams.fmted_keys  # type: ignore[no-any-return]

    @property
    def granules(self):
        """
        Return the granules object, which provides the underlying functionality for searching, ordering,
        and downloading granules for the specified product.
        Users are encouraged to use the built-in wrappers
        rather than trying to access the granules object themselves.

        See Also
        --------
        avail_granules
        order_granules
        download_granules
        granules.Granules

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.granules # doctest: +SKIP
        <icepyx.core.granules.Granules at [location]>
        """

        if not hasattr(self, "_granules") or self._granules is None:
            self._granules = Granules()

        return self._granules

    @cached_property
    def concept_id(self) -> Union[str, None]:
        if hasattr(self, "product"):
            short_name = self.product
        else:
            raise ValueError("Product not defined")
        if hasattr(self, "_version"):
            version = self._version
        else:
            version = is2ref.latest_version(short_name)
        collections = earthaccess.search_datasets(
            short_name=short_name, version=version, cloud_hosted=True
        )
        if collections:
            return collections[0].concept_id()
        else:
            return None

    @property
    def product(self):
        """
        Return the short name product ID string associated with the query object.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.product
        'ATL06'
        """
        return self._prod

    @property
    def product_version(self):
        """
        Return the product version of the data object.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.product_version
        '006'

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='4')
        >>> reg_a.product_version
        '004'
        """
        return self._version

    @property
    def cycles(self):
        """
        Return the unique ICESat-2 orbital cycle.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.cycles
        ['No orbital parameters set']

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71], cycles=['03','04'], tracks=['0849','0902'])
        >>> reg_a.cycles
        ['03', '04']
        """
        if not hasattr(self, "_cycles"):
            return ["No orbital[cycle] parameters set"]
        else:
            if self._cycles is None:
                return ["No orbital[cycle] parameters set"]

            return sorted(set(self._cycles))

    @property
    def tracks(self):
        """
        Return the unique ICESat-2 Reference Ground Tracks

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.tracks
        ['No orbital parameters set']

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71], cycles=['03','04'], tracks=['0849','0902'])
        >>> reg_a.tracks
        ['0849', '0902']
        """
        if not hasattr(self, "_tracks"):
            return ["No orbital[tracks] parameters set"]
        else:
            if self._tracks is None:
                return ["No orbital[tracks] parameters set"]
            return sorted(set(self._tracks))

    # ----------------------------------------------------------------------
    # Methods - Get and display neatly information at the product level
    def __str__(self):
        str = "Product {2} v{3}\n{0}\nDate range {1}".format(
            self.spatial_extent, self.dates, self.product, self.product_version
        )
        return str

    def product_summary_info(self):
        """
        Display a summary of selected metadata for the specified version of the product
        of interest (the collection).

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='006')
        >>> reg_a.product_summary_info()
        title :  ATLAS/ICESat-2 L3A Land Ice Height V006
        short_name :  ATL06
        version_id :  006
        time_start :  2018-10-14T00:00:00.000Z
        coordinate_system :  CARTESIAN
        summary :  This data set (ATL06) provides geolocated, land-ice surface heights (above the WGS 84 ellipsoid, ITRF2014 reference frame), plus ancillary parameters that can be used to interpret and assess the quality of the height estimates. The data were acquired by the Advanced Topographic Laser Altimeter System (ATLAS) instrument on board the Ice, Cloud and land Elevation Satellite-2 (ICESat-2) observatory.
        orbit_parameters :  {}
        """
        if not hasattr(self, "_about_product"):
            self._about_product = is2ref.about_product(self._prod)
        summ_keys = [
            "title",
            "short_name",
            "version_id",
            "time_start",
            "coordinate_system",
            "summary",
            "orbit_parameters",
        ]
        for key in summ_keys:
            print(key, ": ", self._about_product["feed"]["entry"][-1][key])

    def product_all_info(self):
        """
        Display all metadata about the product of interest (the collection).

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.product_all_info() # doctest: +SKIP
        {very long prettily-formatted dictionary output}

        """
        if not hasattr(self, "_about_product"):
            self._about_product = is2ref.about_product(self._prod)
        pprint(self._about_product)

    def latest_version(self):
        """
        A reference function to is2ref.latest_version.

        Determine the most recent version available for the given product.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.latest_version()
        '006'
        """
        return is2ref.latest_version(self.product)

    # DevGoal: add testing? What do we test, and how, given this is a visualization.
    # DevGoal(long term): modify this to accept additional inputs, etc.
    # DevGoal: move this to it's own module for visualizing, etc.
    # DevGoal: see Amy's data access notebook for a zoomed in map - implement here?
    def visualize_spatial_extent(
        self,
    ):  # additional args, basemap, zoom level, cmap, export
        """
        Creates a map displaying the input spatial extent

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06','path/spatialfile.shp',['2019-02-22','2019-02-28']) # doctest: +SKIP
        >>> reg_a.visualize_spatial_extent # doctest: +SKIP
        [visual map output]
        """

        gdf = self._spatial.extent_as_gdf

        try:
            import geoviews as gv  # type: ignore[import]
            from shapely.geometry import Polygon  # noqa: F401

            gv.extension("bokeh")  # pyright: ignore[reportCallIssue]

            bbox_poly = gv.Path(gdf["geometry"]).opts(color="red", line_color="red")
            tile = gv.tile_sources.EsriImagery.opts(width=500, height=500)
            return tile * bbox_poly  # pyright: ignore[reportOperatorIssue]

        except ImportError:
            legacy_url = "https://github.com/geopandas/geopandas/raw/refs/heads/0.8.x/geopandas/datasets/naturalearth_lowres/naturalearth_lowres.shp"
            world = gpd.read_file(legacy_url)  # pyright: ignore[reportAttributeAccessIssue]
            f, ax = plt.subplots(1, figsize=(12, 8))
            world.plot(ax=ax, facecolor="lightgray", edgecolor="gray")
            gdf.plot(ax=ax, color="#FF8C00", alpha=0.7, aspect="equal")
            plt.show()

    def visualize_elevation(self):
        """
        Visualize elevation requested from OpenAltimetry API using datashader based on cycles
        https://holoviz.org/tutorial/Large_Data.html

        Returns
        -------
        map_cycle, map_rgt + lineplot_rgt : Holoviews objects
            Holoviews data visualization elements
        """
        viz = Visualize(self)
        cycle_map, rgt_map = viz.viz_elevation()

        return cycle_map, rgt_map

    def _get_concept_id(self, product, version) -> Union[str, None]:
        """
        Get the concept ID for the specified product and version. Note that we are forcing CMR to use the cloud copy.
        """
        collections = earthaccess.search_datasets(
            short_name=product, version=version, cloud_hosted=True
        )
        if collections:
            return collections[0].concept_id()
        else:
            return None

    # DevGoal: check to make sure the see also bits of the docstrings work properly in RTD
    def avail_granules(self, ids=False, cycles=False, tracks=False, cloud=False):
        """
        Obtain information about the available granules for the query
        object's parameters. By default, a complete list of available granules is
        obtained and stored in the object, but only summary information is returned.
        Lists of granule IDs, cycles and RGTs can be obtained using the boolean triggers.

        Parameters
        ----------
        ids : bool, default False
            Indicates whether the function should return a list of granule IDs.

        cycles : bool, default False
            Indicates whether the function should return a list of orbital cycles.

        tracks : bool, default False
            Indicates whether the function should return a list of RGTs.

        cloud : bool, default False
            Indicates whether the function should return data available in the cloud.
            Note: except in rare cases while data is in the process of being appended to,
            data available in the cloud and for download via on-premesis will be identical.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.avail_granules()
        {'Number of available granules': 4,
        'Average size of granules (MB)': np.float64(55.166646003723145),
        'Total size of all granules (MB)': 220.66658401489258}

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-23'])
        >>> reg_a.avail_granules(ids=True)
        [['ATL06_20190221121851_08410203_006_01.h5', 'ATL06_20190222010344_08490205_006_01.h5']]
        >>> reg_a.avail_granules(cycles=True)
        [['02', '02']]
        >>> reg_a.avail_granules(tracks=True)
        [['0841', '0849']]
        """

        #         REFACTOR: add test to make sure there's a session
        if not hasattr(self, "_granules"):
            self.granules
        try:
            self.granules.avail
        except AttributeError:
            self.granules.get_avail(self.CMRparams)

        if ids or cycles or tracks or cloud:
            # list of outputs in order of ids, cycles, tracks, cloud
            return gran_IDs(
                self.granules.avail,
                ids=ids,
                cycles=cycles,
                tracks=tracks,
                cloud=cloud,
            )
        else:
            return self.granules.avail

    def _order_subset_granules(self, skip_preview: bool = False) -> str:
        concept_id = self._get_concept_id(
            product=self._prod,
            version=self._version,
        )

        if concept_id is None:
            raise ValueError(
                f"Could not find concept ID for {self._prod} v{self._version}"
            )

        readable_granule_name = self.CMRparams.get("readable_granule_name[]", [])
        harmony_temporal = None
        harmony_spatial = None
        if self._temporal:
            # TODO: this assumes there will always be a start and stop
            # temporal range. Harmony can accept start without stop and
            # vice versa.
            harmony_temporal = HarmonyTemporal(
                start=self._temporal.start,
                stop=self._temporal.end,
            )
        if self.spatial:
            if self.spatial.extent_type == "bounding_box":
                # Bounding box case.

                # TODO: think more about how this can be DRYed out. We call
                # `place_order` based on the user spatial input. The bounding box case
                # is simple, but polygons are more complicated because `harmony-py`
                # expects a shapefile (e.g,. geojson) to exist on disk.
                harmony_spatial = harmony.BBox(
                    w=self.spatial.extent[0],
                    s=self.spatial.extent[1],
                    e=self.spatial.extent[2],
                    n=self.spatial.extent[3],
                )
            elif self.spatial.extent_file or self.spatial.extent_type == "polygon":
                harmony_spatial = self.spatial.extent_as_gdf.iloc[0].geometry.wkt
                # Polygons must be passed to `harmony-py` as a path to a valid
                # shapefile (json, geojson, kml, shz, or zip). Create a temporary
                # directory to store this file for the harmony order.
            else:
                raise NotImplementedError(
                    "Only bounding box and polygon spatial subsetting is supported."
                )
        else:
            if harmony_temporal is None:
                raise ValueError("No temporal or spatial parameters provided.")

        job_id = self.harmony_api.place_order(
            concept_id=concept_id,
            temporal=harmony_temporal,
            spatial=harmony_spatial,
            granule_name=list(readable_granule_name),
            skip_preview=skip_preview,
        )
        return job_id

    def _get_granule_links(self, cloud_hosted=False) -> list[str]:
        """
        Get the links to the granules for the query object. This is a blocking call

        Parameters
        ----------
        cloud_hosted : bool, default False
            If True, download the cloud-hosted version of the granules. Otherwise, download
            the on-premises version. We need to run the code in the AWS cloud (us-west-2)

        """
        links = []
        if not hasattr(self.granules, "avail"):
            self.granules.get_avail(self.CMRparams)
        for granule in self.granules.avail:
            for link in granule["links"]:
                if (
                    cloud_hosted
                    and link["rel"] == "http://esipfed.org/ns/fedsearch/1.1/s3#"
                    or (
                        (link["rel"] == "http://esipfed.org/ns/fedsearch/1.1/data#")
                        and (
                            "type" in link
                            and link["type"]
                            in ["application/x-hdf5", "application/x-hdfeos"]
                        )
                    )
                ):
                    links.append(link["href"])
        return links

    def _order_whole_granules(self, cloud_hosted=False) -> list[str]:
        """
        Downloads the whole granules for the query object. This is not an asnc operation
        and will block until the download is complete.

        Parameters
        ----------
        cloud_hosted : bool, default False
            If True, download the cloud-hosted version of the granules. Otherwise, download
            the on-premises version. We need to run the code in the AWS cloud (us-west-2)
        path : str, default "./"
            The local directory to download the granules to.

        """

        links = self._get_granule_links(cloud_hosted=cloud_hosted)
        return links

    def skip_preview(self):
        """
        Skips preview for current order, if it is in preview state.
        Orders with more than 300 granules are automatically put into preview state, which pauses the processing (subsetting).

        """
        if self.last_order and self.last_order.type == "subset":
            status = self.last_order.status()
            if status["status"] == "PREVIEW":
                return self.last_order.resume()

    def order_granules(
        self, subset: bool = True, skip_preview: bool = False
    ) -> DataOrder:
        """
        Place an order for the available granules for the query object.

        Parameters
        ----------
        subset : bool, default True
            Apply subsetting to the data order using harmony, returning only data that meets the
            subset parameters. Spatial and temporal subsetting based on the input parameters happens
            by default when subset=True, but additional subsetting options are available.
            Spatial subsetting returns all data that are within the area of interest (but not complete
            granules. This eliminates false-positive granules returned by the metadata-level search)
        skip_preview : bool, default False
            If True, bypass the preview state when we order subsetting queries that exceed 300 granules.

        See Also
        --------
        harmony.place_order

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.order_granules() # doctest: +SKIP
        Harmony job ID:  931355e8-0005-4dff-9c76-7903a5be283d
        [order status output]
        Harmony provided these error messages:
        [if any were returned from the harmony subsetter, e.g. No data found that matched subset constraints.]
        Your harmony order is:  complete
        """

        # only instantiate the client when we are about to order data
        self.harmony_api = HarmonyApi()
        if subset:
            job_id = self._order_subset_granules(skip_preview=skip_preview)
            self.last_order = DataOrder(
                job_id, "subset", self.granules, self.harmony_api
            )
            return self.last_order
        else:
            files = self._order_whole_granules()
            self.last_order = DataOrder("nosubset", "whole", files, self.harmony_api)
            return self.last_order

    def download_granules(
        self,
        path: Path,
        overwrite: bool = False,
    ) -> Union[list[str], None]:
        """
        Download the granules for the order, blocking until they are ready if necessary.

        Parameters
        ----------
        path : str or Path
            The directory where granules should be saved.
        overwrite : bool, optional
            Whether to overwrite existing files (default is False).

        Returns
        -------
        list or None
            A list of the downloaded file paths if successful, otherwise None.
        """
        # Order granules based on user selections if restart is False and there
        # are no job IDs registered by the harmony API
        if hasattr(self, "last_order") is None:
            raise ValueError("No order has been placed yet.")
        status = self.last_order.status()
        if status["status"] == "running" or status["status"] == "accepted":
            print(
                (
                    "Your harmony job status is still "
                    f"{status['status']}. Please continue waiting... this may take a few moments."
                )
            )
            while (
                status["status"].startswith("running") or status["status"] == "accepted"
            ):
                sys.stdout.write(".")
                sys.stdout.flush()
                # Requesting the status too often can result in a 500 error.
                time.sleep(self.REQUEST_RETRY_INTERVAL_SECONDS)
                status = self.last_order.status()

        if status["status"] == "complete_with_errors" or status["status"] == "failed":
            print("Harmony provided these error messages:")
            pprint(status["errors"])
            return None
        else:
            return self.last_order.download(path, overwrite=overwrite)
