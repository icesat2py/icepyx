import numpy as np
import datetime as dt
import re
import os
import socket
import requests
import json
import warnings
import pprint
from xml.etree import ElementTree as ET
import time
import zipfile
import io
import math
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import fiona
import h5py
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

from icepyx.core.Earthdata import Earthdata
import icepyx.core.APIformatting as apifmt
import icepyx.core.is2ref as is2ref
import icepyx.core.granules as granules
from icepyx.core.granules import Granules as Granules
#QUESTION: why doesn't from granules import Granules as Granules work, since granules=icepyx.core.granules?
# from icepyx.core.granules import Granules
from icepyx.core.variables import Variables as Variables

#DevGoal: update docs throughout to allow for polygon spatial extent
class Icesat2Data():
    """
    ICESat-2 Data object to query, obtain, and perform basic operations on
    available ICESat-2 datasets using temporal and spatial input parameters.
    Allows the easy input and formatting of search parameters to match the
    NASA NSIDC DAAC and (DevGoal) conversion to multiple data types.

    Parameters
    ----------
    dataset : string
        ICESat-2 dataset ID, also known as "short name" (e.g. ATL03).
        Available datasets can be found at: https://nsidc.org/data/icesat-2/data-sets
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
        Dataset version, given as a 3 digit string. If no version is given, the current
        version is used.
    variables : 

    Returns
    -------
    icesat2data object

    See Also
    --------


    Examples
    --------
    Initializing Icesat2Data with a bounding box.
    >>> reg_a_bbox = [-64, 66, -55, 72]
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> region_a = icepyx.Icesat2Data('ATL06', reg_a_bbox, reg_a_dates)
    >>> region_a
    [show output here after inputting above info and running it]

    Initializing Icesat2Data with a list of polygon vertex coordinate pairs.
    >>> reg_a_poly = [(-64, 66), (-64, 72), (-55, 72), (-55, 66), (-64, 66)]
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> region_a = icepyx.Icesat2Data('ATL06', reg_a_poly, reg_a_dates)
    >>> region_a
    [show output here after inputting above info and running it]

    Initializing Icesat2Data with a geospatial polygon file.
    >>> aoi = '/User/name/location/aoi.shp'
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> region_a = icepyx.Icesat2Data('ATL06', aoi, reg_a_dates)
    >>> region_a
    [show output here after inputting above info and running it]

    """

    # ----------------------------------------------------------------------
    # Constructors

    def __init__(
        self,
        dataset = None,
        spatial_extent = None,
        date_range = None,
        start_time = None,
        end_time = None,
        version = None,
        files = None,
    ):

        if (dataset is None or spatial_extent is None or date_range is None) and files is None:
            raise ValueError("Please provide the required inputs. Use help([function]) to view the function's documentation")

        if files is not None:
            self._source = 'files'
            # self.file_vars = Variables(self._source)
        else:
            self._source = 'order'
            # self.order_vars = Variables(self._source)
        # self.variables = Variables(self._source)

        self._dset = is2ref._validate_dataset(dataset)

        if isinstance(spatial_extent, list):
            #bounding box
            if len(spatial_extent)==4 and all(type(i) in [int, float] for i in spatial_extent):
                assert -90 <= spatial_extent[1] <= 90, "Invalid latitude value"
                assert -90 <= spatial_extent[3] <= 90, "Invalid latitude value"
                assert -180 <= spatial_extent[0] <= 360, "Invalid longitude value" #tighten these ranges depending on actual allowed inputs
                assert -180 <= spatial_extent[2] <= 360, "Invalid longitude value"
                assert spatial_extent[0] <= spatial_extent[2], "Invalid bounding box longitudes"
                assert spatial_extent[1] <= spatial_extent[3], "Invalid bounding box latitudes"
                self._spat_extent = spatial_extent
                self.extent_type = 'bounding_box'
            
            #user-entered polygon as list of lon, lat coordinate pairs
            elif all(type(i) in [list, tuple] for i in spatial_extent):
                assert len(spatial_extent)>=4, "Your spatial extent polygon has too few vertices"
                assert spatial_extent[0][0] == spatial_extent[-1][0], "Starting longitude doesn't match ending longitude"
                assert spatial_extent[0][1] == spatial_extent[-1][1], "Starting latitude doesn't match ending latitude"
                polygon = (','.join([str(c) for xy in spatial_extent for c in xy])).split(",")
                polygon = [float(i) for i in polygon]
                self._spat_extent = polygon
                self.extent_type = 'polygon'
                #DevGoal: properly format this input type (and any polygon type) so that it is clockwise (and only contains 1 pole)!!
                warnings.warn("this type of input is not yet well handled and you may not be able to find data")

            #user-entered polygon as a single list of lon and lat coordinates
            elif all(type(i) in [int, float] for i in spatial_extent):
                assert len(spatial_extent)>=8, "Your spatial extent polygon has too few vertices"
                assert len(spatial_extent)%2 == 0, "Your spatial extent polygon list should have an even number of entries"
                assert spatial_extent[0] == spatial_extent[-2], "Starting longitude doesn't match ending longitude"
                assert spatial_extent[1] == spatial_extent[-1], "Starting latitude doesn't match ending latitude"
                polygon = [float(i) for i in spatial_extent]
                self._spat_extent = polygon
                self.extent_type = 'polygon'

            else:
                raise ValueError('Your spatial extent does not meet minimum input criteria')
            
            #DevGoal: write a test for this
            #make sure there is nothing set to self._geom_filepath since its existence determines later steps
            if hasattr(self,'_geom_filepath'):
                del self._geom_filepath

        elif isinstance(spatial_extent, str):
            assert os.path.exists(spatial_extent), "Check that the path and filename of your geometry file are correct"
            #DevGoal: more robust polygon inputting (see Bruce's code): correct for clockwise/counterclockwise coordinates, deal with simplification, etc.
            if spatial_extent.split('.')[-1] in ['kml','shp','gpkg']:
                self.extent_type = 'polygon'
                self._spat_extent = apifmt._format_polygon(spatial_extent)
                self._geom_filepath = spatial_extent

            else:
                raise TypeError('Input spatial extent file must be a kml, shp, or gpkg')

        if isinstance(date_range, list):
            if len(date_range)==2:
                self._start = dt.datetime.strptime(date_range[0], '%Y-%m-%d')
                self._end = dt.datetime.strptime(date_range[1], '%Y-%m-%d')
                assert self._start.date() <= self._end.date(), "Your date range is invalid"

            else:
                raise ValueError("Your date range list is the wrong length. It should have start and end dates only.")

#DevGoal: accept more date/time input formats
#         elif isinstance(date_range, date-time object):
#             print('it is a date-time object')
#         elif isinstance(date_range, dict):
#             print('it is a dictionary. now check the keys for start and end dates')


        if start_time is None:
            self._start = self._start.combine(self._start.date(),dt.datetime.strptime('00:00:00', '%H:%M:%S').time())
        else:
            if isinstance(start_time, str):
                self._start = self._start.combine(self._start.date(),dt.datetime.strptime(start_time, '%H:%M:%S').time())
            else:
                raise TypeError("Please enter your start time as a string")

        if end_time is None:
            self._end = self._start.combine(self._end.date(),dt.datetime.strptime('23:59:59', '%H:%M:%S').time())
        else:
            if isinstance(end_time, str):
                self._end = self._start.combine(self._end.date(),dt.datetime.strptime(end_time, '%H:%M:%S').time())
            else:
                raise TypeError("Please enter your end time as a string")

        latest_vers = self.latest_version()
        if version is None:
            self._version = latest_vers
        else:
            if isinstance(version, str):
                assert int(version)>0, "Version number must be positive"
                vers_length = 3
                self._version = version.zfill(vers_length)
            else:
                raise TypeError("Please enter the version number as a string")

            if int(self._version) < int(latest_vers):
                warnings.filterwarnings("always")
                warnings.warn("You are using an old version of this dataset")



    # ----------------------------------------------------------------------
    # Properties

    @property
    def dataset(self):
        """
        Return the short name dataset ID string associated with the ICESat-2 data object.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.dataset
        ATL06
        """
        return self._dset

    @property
    def dataset_version(self):
        """
        Return the dataset version of the data object.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.dataset_version
        002

        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1')
        >>> region_a.dataset_version
        001
        """
        return self._version

    @property
    def spatial_extent(self):
        """
        Return an array showing the spatial extent of the ICESat-2 data object.
        Spatial extent is returned as an input type (which depends on how
        you initially entered your spatial data) followed by the geometry data.
        Bounding box data is [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        Polygon data is [[list of longitudes],[list of corresponding latitudes]].

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.spatial_extent
        ['bounding box', [-64, 66, -55, 72]]
        """

        if self.extent_type == 'bounding_box':
            return ['bounding box', self._spat_extent]
        elif self.extent_type == 'polygon':
            return ['polygon', [self._spat_extent[0::2], self._spat_extent[1::2]]]
        else:
            return ['unknown spatial type', None]

    @property
    def dates(self):
        """
        Return an array showing the date range of the ICESat-2 data object.
        Dates are returned as an array containing the start and end datetime objects, inclusive, in that order.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.dates
        ['2019-02-22', '2019-02-28']
        """
        return [self._start.strftime('%Y-%m-%d'), self._end.strftime('%Y-%m-%d')] #could also use self._start.date()

    @property
    def start_time(self):
        """
        Return the start time specified for the start date.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.start_time
        00:00:00

        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], start_time='12:30:30')
        >>> region_a.start_time
        12:30:30
        """
        return self._start.strftime('%H:%M:%S')

    @property
    def end_time(self):
        """
        Return the end time specified for the end date.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.end_time
        23:59:59

        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], end_time='10:20:20')
        >>> region_a.end_time
        10:20:20
        """
        return self._end.strftime('%H:%M:%S')

    #DevGoal: add to tests
    #REFACTOR: split into two properties? order_vars and file_vars?
    @property
    def variables(self):
        """
        Return a list of the variables contained in the dataset (not all available variables). 
        The variable list is generated either when a set of data files are opened or data is 
        ordered from the NSIDC.

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> session = region_a.earthdata_login(user_id,user_email)
        >>> region_a.order_granules(session)
        >>> region_a.variables
        """
        
        if not hasattr(self, '_variables'):
            if self._source == 'order':
                #DevGoal: check for active session here
                if hassattr(self, '_cust_options'):
                    self._variables = Variables(self._source, session=self._session, avail=self._cust_options['variables'])
                else:
                    self._variables = Variables(self._source, session=self._session, /
                    dataset=self.dataset, version=self._version)
            elif: self._source == 'file':
                self._variables = Variables(self._source)

        return self._variables
        print(self._variables)
        
        # try:
        #     if hasattr(self, '_variables'):
        #         return self._variables
        # except NameError:
        #     return AttributeError('You must generate a list of wanted variables with `build_wanted_var_list`, place a data order, or bring in a set of data files to populate this parameter')
        #this information can be populated in three ways: 0 (implemented) generate a list of variables for the subsetter 1 (not yet implemented) by having the user submit an order for data; 2 (not yet implemented) by bringing in existing data files into a class object
        

    # ----------------------------------------------------------------------
    # Static Methods

    # ----------------------------------------------------------------------
    # Methods - Get and display neatly information at the dataset level

    def _about_dataset(self):
        """
        Ping Earthdata to get metadata about the dataset of interest (the collection).
        """

        cmr_collections_url = 'https://cmr.earthdata.nasa.gov/search/collections.json'
        response = requests.get(cmr_collections_url, params={'short_name': self._dset})
        results = json.loads(response.content)
        return results

    def dataset_summary_info(self):
        """
        Display a summary of selected metadata for the most specified version of the dataset 
        of interest (the collection).
        """
        summ_keys = ['dataset_id', 'short_name', 'version_id', 'time_start', 'coordinate_system', 'summary', 'orbit_parameters']
        for key in summ_keys:
            print(key,': ',self._about_dataset()['feed']['entry'][int(self._version)-1][key])

    def dataset_all_info(self):
        """
        Display all metadata about the dataset of interest (the collection).
        """
        pprint.pprint(self._about_dataset())

    def latest_version(self):
        """
        Determine the most recent version available for the given dataset.
        """
        dset_info = self._about_dataset()
        return max([entry['version_id'] for entry in dset_info['feed']['entry']])

    def show_custom_options(self, session, dictview=False):
        """
        Display customization/subsetting options available for this dataset.
        
        Parameters
        ----------
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object can be obtained using is2_data.earthdata_login(uid, email) and entering your
            Earthdata login password when prompted. You must have previously registered for an Earthdata account.

        dictview : boolean, default False
            Show the variable portion of the custom options list as a dictionary with key:value
            pairs representing variable:paths-to-variable rather than as a long list of full
            variable paths.
        
        """
        headers=['Subsetting options', 'Data File Formats (Reformatting Options)', 'Reprojection Options',
                 'Data File (Reformatting) Options Supporting Reprojection',
                 'Data File (Reformatting) Options NOT Supporting Reprojection',
                 'Data Variables (also Subsettable)']
        keys=['options', 'fileformats', 'reprojectionONLY', 'formatreproj', 'noproj', 'variables']

        try:
            all(key in self._cust_options.keys() for key in keys)
        except AttributeError or KeyError:
            self._cust_options=is2ref._get_custom_options(session, self.dataset, self._version)

        for h,k in zip(headers,keys):
            print(h)
            if k=='variables' and dictview:
                vgrp,paths = Variables._parse_var_list(self._cust_options[k])
                pprint.pprint(vgrp)
            else:
                pprint.pprint(self._cust_options[k])

  

    # ----------------------------------------------------------------------
    # Methods - - Generate and format information for submitting to API (non-general)

   

    # ----------------------------------------------------------------------
    # Methods - Interact with NSIDC-API

    def earthdata_login(self,uid,email):
        if not hasattr(self,'reqparams'):
            self.reqparams={}
        self.reqparams.update({'email': email}) #REFACTOR-need this?, 'token': token})
        capability_url = f'https://n5eil02u.ecs.nsidc.org/egi/capabilities/{self.dataset}.{self._version}.xml'
        self._session = Earthdata(uid,email,capability_url).login()
        print(self._session)
        self.variables = Variables(self._source, session=self._session)
        return self._session

    def avail_granules(self):
        """
        Get a list of available granules for the ICESat-2 data object's parameters
        """
        #REFACTOR: add test to make sure there's a session
        self.granules = Granules(session=self._session)
        apifmt.build_CMR_params(self)
        apifmt.build_reqconfig_params(self,'search')

        self.granules.get_avail(self.CMRparams,self.reqparams)
        # self.granules = Granules.get_avail(self.CMRparams,self.reqparams)

        return granules.info(self.granules.avail)


    #DevGoal: display output to indicate number of granules successfully ordered (and number of errors)
    #DevGoal: deal with subset=True for variables now, and make sure that if a variable subset Coverage kwarg is input it's successfully passed through all other functions even if this is the only one run.
    def order_granules(self, verbose=False, subset=True, **kwargs):
        """
        Place an order for the available granules for the ICESat-2 data object.
        Adds the list of zipped files (orders) to the data object.
        DevGoal: add additional kwargs to allow subsetting and more control over request options.
        Note: This currently uses paging to download data - this may not be the best method
        You must already be logged in to Earthdata to use this function.

        Parameters
        ----------
        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.

        subset : boolean, default True
            Use input temporal and spatial search parameters to subset each granule and return only data
            that is actually within those parameters (rather than complete granules which may contain only
            a small area of interest).

        kwargs...
        """

        apifmt.build_CMR_params(self)
        apifmt.build_reqconfig_params(self,'download')
        if subset is False:
            self.subsetparams=None
        else:
            apifmt.build_subset_params(self,**kwargs)

        #REFACTOR: add checks here to see if the granules object has been created (if not, need to create one and add session)
        self.granules.place_order(self.CMRparams, self.reqparams, self.subsetparams, verbose, subset, **kwargs)
        # self.orderIDs = granules.place_order(self.CMRparams, self.reqparams, self.subsetparams, /
        #                                     self._session, verbose=verbose, subset=subset, **kwargs)
        #DELETE? DevNote: this may cause issues if you're trying to add to - but not replace - the variable list... should overall make that handle-able
#         try:
#             #DevGoal: make this the dictionary instead of the long string?
#             self._variables = self.subsetparams['Coverage']
#         except KeyError:
#             try:
#                 self._variables = self._cust_options['variables']
#             except AttributeError:
#                 self._get_custom_options(session)
#                 self._variables = self._cust_options['variables']


    def download_granules(self, path, verbose=False): #, extract=False):
        """
        Downloads the data ordered using order_granules.

        Parameters
        ----------
        path : string
            String with complete path to desired download location.
        verbose : boolean, default False
            Print out all feedback available from the download process.
            Progress information is automatically printed regardless of the value of verbose.
        """
        """
        extract : boolean, default False
            Unzip the downloaded granules.
        """
     
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)

        #REFACTOR: check that the attribute/order exists
        self.granules.download(verbose, path)
  

     

    # ----------------------------------------------------------------------
    # Methods - IS2class specific geospatial manipulation and visualization

    #DevGoal: add testing? How do we test this (if it creates a valid dataframe, isn't testing that the dataframe is the one we're creating circular, even if we've constructed the bounding box/polygon again)?
    def geodataframe(self):
        """
        Return a geodataframe of the spatial extent

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> gdf = region_a.geodataframe()
        >>> gdf.geometry
        0    POLYGON ((-64 66, -64 72, -55 72, -55 66, -64 ...
        Name: geometry, dtype: object
        """

        if self.extent_type == 'bounding_box':
            boxx = [self._spat_extent[0], self._spat_extent[0], self._spat_extent[2],\
                    self._spat_extent[2], self._spat_extent[0]]
            boxy = [self._spat_extent[1], self._spat_extent[3], self._spat_extent[3],\
                    self._spat_extent[1], self._spat_extent[1]]
            #DevGoal: check to see that the box is actually correctly constructed; have not checked actual location of test coordinates
            gdf = gpd.GeoDataFrame(geometry=[Polygon(list(zip(boxx,boxy)))])
            return gdf
        elif self.extent_type == 'polygon':
            if isinstance(self._spat_extent,str):
                spat_extent = self._spat_extent.split(',')
            else:
                spat_extent = self._spat_extent
            spatial_extent_geom = Polygon(zip(spat_extent[0::2], spat_extent[1::2]))
            gdf = gpd.GeoDataFrame(index=[0],crs={'init':'epsg:4326'}, geometry=[spatial_extent_geom])
            return gdf
        else:
            raise TypeError("Your spatial extent type (" + self.extent_type + ") is not an accepted input and a geodataframe cannot be constructed")

    #DevGoal: add testing? What do we test, and how, given this is a visualization.
    #DevGoal(long term): modify this to accept additional inputs, etc.
    def visualize_spatial_extent(self): #additional args, basemap, zoom level, cmap, export
        """
        Creates a map of the input spatial extent

        Examples
        --------
        >>> icepyx.Icesat2Data('ATL06','path/spatialfile.shp',['2019-02-22','2019-02-28'])
        >>> region_a.visualize_spatial_extent
        """

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        f, ax = plt.subplots(1, figsize=(12, 6))
        world.plot(ax=ax, facecolor='lightgray', edgecolor='gray')
        self.geodataframe().plot(ax=ax, color='#FF8C00',alpha = '0.7')
        plt.show()
