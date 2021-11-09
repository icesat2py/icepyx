import datetime as dt
import os
import requests
import json
import warnings
import pprint
import time
import geopandas as gpd
import matplotlib.pyplot as plt

from icepyx.core.Earthdata import Earthdata
import icepyx.core.APIformatting as apifmt
import icepyx.core.is2ref as is2ref
import icepyx.core.granules as granules
from icepyx.core.granules import Granules as Granules

# QUESTION: why doesn't from granules import Granules as Granules work, since granules=icepyx.core.granules?
# from icepyx.core.granules import Granules
from icepyx.core.variables import Variables as Variables
import icepyx.core.geospatial as geospatial
import icepyx.core.validate_inputs as val
from icepyx.core.visualization import Visualize

# DevGoal: update docs throughout to allow for polygon spatial extent
# Note: add files to docstring once implemented
# DevNote: currently this class is not tested
class Query:
    """
    ICESat-2 Data object to query, obtain, and perform basic operations on
    available ICESat-2 data products using temporal and spatial input parameters.
    Allows the easy input and formatting of search parameters to match the
    NASA NSIDC DAAC and (development goal-not yet implemented) conversion to multiple data types.

    Parameters
    ----------
    product : string
        ICESat-2 data product ID, also known as "short name" (e.g. ATL03).
        Available data products can be found at: https://nsidc.org/data/icesat-2/data-sets
    spatial_extent : list or string
        Spatial extent of interest, provided as a bounding box, list of polygon coordinates, or
        geospatial polygon file.
        Bounding box coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        Polygon coordinates should be provided as coordinate pairs in decimal degrees as
        [(longitude1, latitude1), (longitude2, latitude2), ... (longitude_n,latitude_n), (longitude1,latitude1)]
        or
        [longitude1, latitude1, longitude2, latitude2, ... longitude_n,latitude_n, longitude1,latitude1].
        Your list must contain at least four points, where the first and last are identical.
        DevGoal: adapt code so the polygon is automatically closed if need be
        Geospatial polygon files are entered as strings with the full file path and
        must contain only one polygon with the area of interest.
        Currently supported formats are: kml, shp, and gpkg
    date_range : list of 'YYYY-MM-DD' strings
        Date range of interest, provided as start and end dates, inclusive.
        The required date format is 'YYYY-MM-DD' strings, where
        YYYY = 4 digit year, MM = 2 digit month, DD = 2 digit day.
        Currently, a list of specific dates (rather than a range) is not accepted.
        DevGoal: accept date-time objects, dicts (with 'start_date' and 'end_date' keys, and DOY inputs).
        DevGoal: allow searches with a list of dates, rather than a range.
    start_time : HH:mm:ss, default 00:00:00
        Start time in UTC/Zulu (24 hour clock). If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    end_time : HH:mm:ss, default 23:59:59
        End time in UTC/Zulu (24 hour clock). If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    version : string, default most recent version
        Product version, given as a 3 digit string. If no version is given, the current
        version is used. Example: "004"
    cycles : string or a list of strings, default all available orbital cycles
        Product cycle, given as a 2 digit string. If no cycle is given, all available
        cycles are used. Example: "04"
    tracks : string or a list of strings, default all available reference ground tracks (RGTs)
        Product track, given as a 4 digit string. If no track is given, all available
        reference ground tracks are used. Example: "0594"
    files : string, default None
        A placeholder for future development. Not used for any purposes yet.

    Returns
    -------
    query object

    Examples
    --------
    Initializing Query with a bounding box.

    >>> reg_a_bbox = [-55, 68, -48, 71]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = icepyx.query.Query('ATL06', reg_a_bbox, reg_a_dates)
    >>> reg_a
    <icepyx.core.query.Query at [location]>

    Initializing Query with a list of polygon vertex coordinate pairs.

    >>> reg_a_poly = [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = icepyx.query.Query('ATL06', reg_a_poly, reg_a_dates)
    >>> reg_a
    <icepyx.core.query.Query at [location]>

    Initializing Query with a geospatial polygon file.

    >>> aoi = '/User/name/location/aoi.shp'
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> reg_a = icepyx.query.Query('ATL06', aoi, reg_a_dates)
    >>> reg_a
    <icepyx.core.query.Query at [location]>
    """

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
        files=None,  # NOTE: if you end up implemeting this feature here, use a better variable name than "files"
    ):

        # warnings.filterwarnings("always")
        # warnings.warn("Please note: as of 2020-05-05, a major reorganization of the core icepyx.query code may result in errors produced by now depricated functions. Please see our documentation pages or example notebooks for updates.")

        if (
            (product is None or spatial_extent is None)
            and (date_range is None or cycles is None or tracks is None)
            and files is None
        ):
            raise ValueError(
                "Please provide the required inputs. Use help([function]) to view the function's documentation"
            )

        if files is not None:
            self._source = "files"
            # self.file_vars = Variables(self._source)
        else:
            self._source = "order"
            # self.order_vars = Variables(self._source)
        # self.variables = Variables(self._source)

        self._prod = is2ref._validate_product(product)

        self.extent_type, self._spat_extent, self._geom_filepath = val.spatial(
            spatial_extent
        )

        if date_range:
            self._start, self._end = val.temporal(date_range, start_time, end_time)

        self._version = val.prod_version(self.latest_version(), version)

        # build list of available CMR parameters if reducing by cycle or RGT
        # or a list of explicitly named files (full or partial names)
        # DevGoal: add file name search to optional queries
        if cycles or tracks:
            # get lists of available ICESat-2 cycles and tracks
            self._cycles = val.cycles(cycles)
            self._tracks = val.tracks(tracks)
            # create list of CMR parameters for granule name
            self._readable_granule_name = apifmt._fmt_readable_granules(
                self._prod, cycles=self.cycles, tracks=self.tracks
            )

    # ----------------------------------------------------------------------
    # Properties

    @property
    def dataset(self):
        """
        Legacy property included to provide depracation warning.

        See Also
        --------
        product
        """
        warnings.filterwarnings("always")
        warnings.warn(
            "In line with most common usage, 'dataset' has been replaced by 'product'.",
            DeprecationWarning,
        )

    @property
    def product(self):
        """
        Return the short name product ID string associated with the query object.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
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
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.product_version
        '003'

        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='1')
        >>> reg_a.product_version
        '001'
        """
        return self._version

    @property
    def spatial_extent(self):
        """
        Return an array showing the spatial extent of the query object.
        Spatial extent is returned as an input type (which depends on how
        you initially entered your spatial data) followed by the geometry data.
        Bounding box data is [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        Polygon data is [[array of longitudes],[array of corresponding latitudes]].

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.spatial_extent
        ['bounding box', [-55, 68, -48, 71]]

        >>> reg_a = icepyx.query.Query('ATL06',[(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)],['2019-02-20','2019-02-28'])
        >>> reg_a.spatial_extent
        ['polygon', [-55.0, 68.0, -55.0, 71.0, -48.0, 71.0, -48.0, 68.0, -55.0, 68.0]]
        """

        if self.extent_type == "bounding_box":
            return ["bounding box", self._spat_extent]
        elif self.extent_type == "polygon":
            # return ['polygon', self._spat_extent]
            # Note: self._spat_extent is a shapely geometry object
            return ["polygon", self._spat_extent.exterior.coords.xy]
        else:
            return ["unknown spatial type", None]

    @property
    def dates(self):
        """
        Return an array showing the date range of the query object.
        Dates are returned as an array containing the start and end datetime objects, inclusive, in that order.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.dates
        ['2019-02-20', '2019-02-28']
        """
        if not hasattr(self, "_start"):
            return ["No temporal parameters set"]
        else:
            return [
                self._start.strftime("%Y-%m-%d"),
                self._end.strftime("%Y-%m-%d"),
            ]  # could also use self._start.date()

    @property
    def start_time(self):
        """
        Return the start time specified for the start date.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.start_time
        '00:00:00'

        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], start_time='12:30:30')
        >>> reg_a.start_time
        '12:30:30'
        """
        if not hasattr(self, "_start"):
            return ["No temporal parameters set"]
        else:
            return self._start.strftime("%H:%M:%S")

    @property
    def end_time(self):
        """
        Return the end time specified for the end date.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.end_time
        '23:59:59'

        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], end_time='10:20:20')
        >>> reg_a.end_time
        '10:20:20'
        """
        if not hasattr(self, "_end"):
            return ["No temporal parameters set"]
        else:
            return self._end.strftime("%H:%M:%S")

    @property
    def cycles(self):
        """
        Return the unique ICESat-2 orbital cycle.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.cycles
        ['02']
        """
        if not hasattr(self, "_cycles"):
            return ["No orbital parameters set"]
        else:
            return sorted(set(self._cycles))

    @property
    def tracks(self):
        """
        Return the unique ICESat-2 Reference Ground Tracks

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.tracks
        ['0841', '0849', '0902', '0910']
        """
        if not hasattr(self, "_tracks"):
            return ["No orbital parameters set"]
        else:
            return sorted(set(self._tracks))

    @property
    def CMRparams(self):
        """
        Display the CMR key:value pairs that will be submitted. It generates the dictionary if it does not already exist.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.CMRparams
        {'short_name': 'ATL06',
        'version': '002',
        'temporal': '2019-02-20T00:00:00Z,2019-02-28T23:59:59Z',
        'bounding_box': '-55,68,-48,71'}
        """

        if not hasattr(self, "_CMRparams"):
            self._CMRparams = apifmt.Parameters("CMR")
        # print(self._CMRparams)
        # print(self._CMRparams.fmted_keys)

        # dictionary of optional CMR parameters
        kwargs = {}
        # temporal CMR parameters
        if hasattr(self, "_start") and hasattr(self, "_end"):
            kwargs["start"] = self._start
            kwargs["end"] = self._end
        # granule name CMR parameters (orbital or file name)
        # DevGoal: add to file name search to optional queries
        if hasattr(self, "_readable_granule_name"):
            kwargs["options[readable_granule_name][pattern]"] = "true"
            kwargs["options[spatial][or]"] = "true"
            kwargs["readable_granule_name[]"] = self._readable_granule_name

        if self._CMRparams.fmted_keys == {}:
            self._CMRparams.build_params(
                product=self.product,
                version=self._version,
                extent_type=self.extent_type,
                spatial_extent=self._spat_extent,
                **kwargs,
            )

        return self._CMRparams.fmted_keys

    @property
    def reqparams(self):
        """
        Display the required key:value pairs that will be submitted. It generates the dictionary if it does not already exist.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.reqparams
        {'page_size': 2000, 'page_num': 1}

        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.order_granules()
        >>> reg_a.reqparams
        {'page_size': 2000, 'page_num': 1, 'request_mode': 'async', 'include_meta': 'Y', 'client_string': 'icepyx'}
        """

        if not hasattr(self, "_reqparams"):
            self._reqparams = apifmt.Parameters("required", reqtype="search")
            self._reqparams.build_params()

        return self._reqparams.fmted_keys

    # @property
    # DevQuestion: if I make this a property, I get a "dict" object is not callable when I try to give input kwargs... what approach should I be taking?
    def subsetparams(self, **kwargs):
        """
        Display the subsetting key:value pairs that will be submitted. It generates the dictionary if it does not already exist
        and returns an empty dictionary if subsetting is set to False during ordering.

        Parameters
        ----------
        **kwargs : key-value pairs
            Additional parameters to be passed to the subsetter.
            By default temporal and spatial subset keys are passed.
            Acceptable key values are ['format','projection','projection_parameters','Coverage'].
            At this time (2020-05), only variable ('Coverage') parameters will be automatically formatted.

        See Also
        --------
        order_granules

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.subsetparams()
        {'time': '2019-02-20T00:00:00,2019-02-28T23:59:59', 'bbox': '-55,68,-48,71'}
        """
        if not hasattr(self, "_subsetparams"):
            self._subsetparams = apifmt.Parameters("subset")

        # temporal subsetting parameters
        if hasattr(self, "_start") and hasattr(self, "_end"):
            kwargs["start"] = self._start
            kwargs["end"] = self._end

        if self._subsetparams == None and not kwargs:
            return {}
        else:
            if self._subsetparams == None:
                self._subsetparams = apifmt.Parameters("subset")
            if self._geom_filepath is not None:
                self._subsetparams.build_params(
                    geom_filepath=self._geom_filepath,
                    extent_type=self.extent_type,
                    spatial_extent=self._spat_extent,
                    **kwargs,
                )
            else:
                self._subsetparams.build_params(
                    extent_type=self.extent_type,
                    spatial_extent=self._spat_extent,
                    **kwargs,
                )

            return self._subsetparams.fmted_keys

    # DevGoal: add to tests
    # DevGoal: add statements to the following vars properties to let the user know if they've got a mismatched source and vars type
    @property
    def order_vars(self):
        """
        Return the order variables object.
        This instance is generated when data is ordered from the NSIDC.

        See Also
        --------
        variables.Variables

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.order_vars
        <icepyx.core.variables.Variables at [location]>
        """

        if not hasattr(self, "_order_vars"):
            if self._source == "order":
                # DevGoal: check for active session here
                if hasattr(self, "_cust_options"):
                    self._order_vars = Variables(
                        self._source,
                        session=self._session,
                        product=self.product,
                        avail=self._cust_options["variables"],
                    )
                else:
                    self._order_vars = Variables(
                        self._source,
                        session=self._session,
                        product=self.product,
                        version=self._version,
                    )

        # I think this is where property setters come in, and one should be used here? Right now order_vars.avail is only filled in
        # if _cust_options exists when the class is initialized, but not if _cust_options is filled in prior to another call to order_vars
        # if self._order_vars.avail == None and hasattr(self, '_cust_options'):
        #     print('got into the loop')
        #     self._order_vars.avail = self._cust_options['variables']

        return self._order_vars

    @property
    def file_vars(self):
        """
        Return the file variables object.
        This instance is generated when files are used to create the data object (not yet implemented).

        See Also
        --------
        variables.Variables

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.file_vars
        <icepyx.core.variables.Variables at [location]>
        """

        if not hasattr(self, "_file_vars"):
            if self._source == "file":
                self._file_vars = Variables(self._source, product=self.product)

        return self._file_vars

    @property
    def granules(self):
        """
        Return the granules object, which provides the underlying funtionality for searching, ordering,
        and downloading granules for the specified product. Users are encouraged to use the built in wrappers
        rather than trying to access the granules object themselves.

        See Also
        --------
        avail_granules
        order_granules
        download_granules
        granules.Granules

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.granules
        <icepyx.core.granules.Granules at [location]>
        """

        if not hasattr(self, "_granules"):
            self._granules = Granules()
        elif self._granules == None:
            self._granules = Granules()

        return self._granules

    # ----------------------------------------------------------------------
    # Methods - Get and display neatly information at the product level

    def product_summary_info(self):
        """
        Display a summary of selected metadata for the specified version of the product
        of interest (the collection).

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.product_summary_info()
        title :  ATLAS/ICESat-2 L3A Land Ice Height V002
        short_name :  ATL06
        version_id :  002
        time_start :  2018-10-14T00:00:00.000Z
        coordinate_system :  CARTESIAN
        summary :  This data set (ATL06) provides geolocated, land-ice surface heights (above the WGS 84 ellipsoid, ITRF2014 reference frame), plus ancillary parameters that can be used to interpret and assess the quality of the height estimates. The data were acquired by the Advanced Topographic Laser Altimeter System (ATLAS) instrument on board the Ice, Cloud and land Elevation Satellite-2 (ICESat-2) observatory.
        orbit_parameters :  {'swath_width': '36.0', 'period': '94.29', 'inclination_angle': '92.0', 'number_of_orbits': '0.071428571', 'start_circular_latitude': '0.0'}
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
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.product_all_info()
        {very long prettily-formatted dictionary output}

        """
        if not hasattr(self, "_about_product"):
            self._about_product = is2ref.about_product(self._prod)
        pprint.pprint(self._about_product)

    def latest_version(self):
        """
        Determine the most recent version available for the given product.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.latest_version()
        '003'
        """
        if not hasattr(self, "_about_product"):
            self._about_product = is2ref.about_product(self._prod)
        return max(
            [entry["version_id"] for entry in self._about_product["feed"]["entry"]]
        )

    def show_custom_options(self, dictview=False):
        """
        Display customization/subsetting options available for this product.

        Parameters
        ----------
        dictview : boolean, default False
            Show the variable portion of the custom options list as a dictionary with key:value
            pairs representing variable:paths-to-variable rather than as a long list of full
            variable paths.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.show_custom_options(dictview=True):
        Subsetting options
        [{'id': 'ICESAT2',
        'maxGransAsyncRequest': '2000',
        'maxGransSyncRequest': '100',
        'spatialSubsetting': 'true',
        'spatialSubsettingShapefile': 'true',
        'temporalSubsetting': 'true',
        'type': 'both'}]
        Data File Formats (Reformatting Options)
        ['TABULAR_ASCII', 'NetCDF4-CF', 'Shapefile', 'NetCDF-3']
        Reprojection Options
        []
        Data File (Reformatting) Options Supporting Reprojection
        ['TABULAR_ASCII', 'NetCDF4-CF', 'Shapefile', 'NetCDF-3', 'No reformatting']
        Data File (Reformatting) Options NOT Supporting Reprojection
        []
        Data Variables (also Subsettable)
        ['ancillary_data/atlas_sdp_gps_epoch',
        'ancillary_data/control',
        'ancillary_data/data_end_utc',
        .
        .
        .
        'quality_assessment/gt3r/signal_selection_source_fraction_3']
        """
        headers = [
            "Subsetting options",
            "Data File Formats (Reformatting Options)",
            "Reprojection Options",
            "Data File (Reformatting) Options Supporting Reprojection",
            "Data File (Reformatting) Options NOT Supporting Reprojection",
            "Data Variables (also Subsettable)",
        ]
        keys = [
            "options",
            "fileformats",
            "reprojectionONLY",
            "formatreproj",
            "noproj",
            "variables",
        ]

        try:
            all(key in self._cust_options.keys() for key in keys)
        except AttributeError or KeyError:
            self._cust_options = is2ref._get_custom_options(
                self._session, self.product, self._version
            )

        for h, k in zip(headers, keys):
            print(h)
            if k == "variables" and dictview:
                vgrp, paths = Variables.parse_var_list(self._cust_options[k])
                pprint.pprint(vgrp)
            else:
                pprint.pprint(self._cust_options[k])

    # ----------------------------------------------------------------------
    # Methods - Login and Granules (NSIDC-API)

    def earthdata_login(self, uid, email, s3token=False):
        """
        Log in to NSIDC EarthData to access data. Generates the needed session and token for most
        data searches and data ordering/download.

        Parameters
        ----------
        uid : string
            Earthdata login user ID
        email : string
            Email address. NSIDC will automatically send you emails about the status of your order.
        s3token : boolean, default False
            Generate AWS s3 ICESat-2 data access credentials

        See Also
        --------
        Earthdata.Earthdata

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        """

        if s3token == False:
            capability_url = f"https://n5eil02u.ecs.nsidc.org/egi/capabilities/{self.dataset}.{self._version}.xml"
        elif s3token == True:

            def is_ec2():
                import socket

                try:
                    socket.gethostbyname("instance-data")
                    return True
                except socket.gaierror:
                    return False

            # loosely check for AWS login capability without web request
            assert (
                is_ec2() == True
            ), "You must be working from a valid AWS instance to use s3 data access"
            capability_url = "https://data.nsidc.earthdatacloud.nasa.gov/s3credentials"

        self._session = Earthdata(uid, email, capability_url).login()

        # DevNote: might make sense to do this part elsewhere in the future, but wanted to get it implemented for now
        if s3token == True:
            self._s3login_credentials = json.loads(
                self._session.get(self._session.get(capability_url).url).content
            )
        self._email = email

    # DevGoal: check to make sure the see also bits of the docstrings work properly in RTD
    def avail_granules(self, ids=False, cycles=False, tracks=False, s3urls=False):
        """
        Obtain information about the available granules for the query
        object's parameters. By default, a complete list of available granules is
        obtained and stored in the object, but only summary information is returned.
        Lists of granule IDs, cycles and RGTs can be obtained using the boolean triggers.

        Parameters
        ----------
        ids : boolean, default False
            Indicates whether the function should return a list of granule IDs.

        cycles : boolean, default False
            Indicates whether the function should return a list of orbital cycles.

        tracks : boolean, default False
            Indicates whether the function should return a list of RGTs.

        s3urls : boolean, default False
            Indicates whether the function should return a list of potential AWS s3 urls.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.avail_granules()
        {'Number of available granules': 4,
        'Average size of granules (MB)': 48.975419759750004,
        'Total size of all granules (MB)': 195.90167903900002}

        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.avail_granules(ids=True)
        >>> reg_a.avail_granules(cycles=True)
        ['02']
        >>> reg_a.avail_granules(tracks=True)
        ['0841', '0849', '0902', '0910']
        """

        #         REFACTOR: add test to make sure there's a session
        if not hasattr(self, "_granules"):
            self.granules
        try:
            self.granules.avail
        except AttributeError:
            self.granules.get_avail(self.CMRparams, self.reqparams)

        if ids or cycles or tracks or s3urls:
            # list of outputs in order of ids, cycles, tracks, s3urls
            return granules.gran_IDs(
                self.granules.avail,
                ids=ids,
                cycles=cycles,
                tracks=tracks,
                s3urls=s3urls,
            )
        else:
            return granules.info(self.granules.avail)

    # DevGoal: display output to indicate number of granules successfully ordered (and number of errors)
    # DevGoal: deal with subset=True for variables now, and make sure that if a variable subset Coverage kwarg is input it's successfully passed through all other functions even if this is the only one run.
    def order_granules(self, verbose=False, subset=True, email=False, **kwargs):
        """
        Place an order for the available granules for the query object.

        Parameters
        ----------
        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.
        subset : boolean, default True
            Apply subsetting to the data order from the NSIDC, returning only data that meets the
            subset parameters. Spatial and temporal subsetting based on the input parameters happens
            by default when subset=True, but additional subsetting options are available.
            Spatial subsetting returns all data that are within the area of interest (but not complete
            granules. This eliminates false-positive granules returned by the metadata-level search)
        email: boolean, default False
            Have NSIDC auto-send order status email updates to indicate order status as pending/completed.
        **kwargs : key-value pairs
            Additional parameters to be passed to the subsetter.
            By default temporal and spatial subset keys are passed.
            Acceptable key values are ['format','projection','projection_parameters','Coverage'].
            The variable 'Coverage' list should be constructed using the `order_vars.wanted` attribute of the object.
            At this time (2020-05), only variable ('Coverage') parameters will be automatically formatted.

        See Also
        --------
        granules.place_order

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.order_granules()
        order ID: [###############]
        [order status output]
        error messages:
        [if any were returned from the NSIDC subsetter, e.g. No data found that matched subset constraints.]
        .
        .
        .
        Retry request status is: complete
        """

        if not hasattr(self, "reqparams"):
            self.reqparams

        if self._reqparams._reqtype == "search":
            self._reqparams._reqtype = "download"

        if "email" in self._reqparams.fmted_keys.keys() or email == False:
            self._reqparams.build_params(**self._reqparams.fmted_keys)
        else:
            self._reqparams.build_params(
                **self._reqparams.fmted_keys, email=self._email
            )

        if subset is False:
            self._subsetparams = None
        elif (
            subset == True
            and hasattr(self, "_subsetparams")
            and self._subsetparams == None
        ):
            del self._subsetparams

        # REFACTOR: add checks here to see if the granules object has been created, and also if it already has a list of avail granules (if not, need to create one and add session)
        if not hasattr(self, "_granules"):
            self.granules
        self._granules.place_order(
            self.CMRparams,
            self.reqparams,
            self.subsetparams(**kwargs),
            verbose,
            subset,
            session=self._session,
            geom_filepath=self._geom_filepath,
        )

    # DevGoal: put back in the kwargs here so that people can just call download granules with subset=False!
    def download_granules(
        self, path, verbose=False, subset=True, restart=False, **kwargs
    ):  # , extract=False):
        """
        Downloads the data ordered using order_granules.

        Parameters
        ----------
        path : string
            String with complete path to desired download location.
        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.
        subset : boolean, default True
            Apply subsetting to the data order from the NSIDC, returning only data that meets the
            subset parameters. Spatial and temporal subsetting based on the input parameters happens
            by default when subset=True, but additional subsetting options are available.
            Spatial subsetting returns all data that are within the area of interest (but not complete
            granules. This eliminates false-positive granules returned by the metadata-level search)
        restart: boolean, default false
            If previous download was terminated unexpectedly. Run again with restart set to True to continue.
        **kwargs : key-value pairs
            Additional parameters to be passed to the subsetter.
            By default temporal and spatial subset keys are passed.
            Acceptable key values are ['format','projection','projection_parameters','Coverage'].
            The variable 'Coverage' list should be constructed using the `order_vars.wanted` attribute of the object.
            At this time (2020-05), only variable ('Coverage') parameters will be automatically formatted.

        See Also
        --------
        granules.download
        """
        """
        extract : boolean, default False
            Unzip the downloaded granules.

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.download_granules('/path/to/download/folder')
        Beginning download of zipped output...
        Data request [##########] of x order(s) is complete.
        """

        # if not os.path.exists(path):
        #     os.mkdir(path)
        # os.chdir(path)

        if not hasattr(self, "_granules"):
            self.granules

        if restart == True:
            pass
        else:
            if (
                not hasattr(self._granules, "orderIDs")
                or len(self._granules.orderIDs) == 0
            ):
                self.order_granules(verbose=verbose, subset=subset, **kwargs)

        self._granules.download(verbose, path, session=self._session, restart=restart)

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
        >>> icepyx.query.Query('ATL06','path/spatialfile.shp',['2019-02-22','2019-02-28'])
        >>> reg_a.visualize_spatial_extent
        [visual map output]
        """
        gdf = geospatial.geodataframe(self.extent_type, self._spat_extent)

        try:
            from shapely.geometry import Polygon
            import geoviews as gv

            gv.extension("bokeh")

            line_geoms = Polygon(gdf["geometry"][0]).boundary
            bbox_poly = gv.Path(line_geoms).opts(color="red", line_color="red")
            tile = gv.tile_sources.EsriImagery.opts(width=500, height=500)
            return tile * bbox_poly

        except ImportError:
            world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
            f, ax = plt.subplots(1, figsize=(12, 6))
            world.plot(ax=ax, facecolor="lightgray", edgecolor="gray")
            gdf.plot(ax=ax, color="#FF8C00", alpha=0.7)
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
