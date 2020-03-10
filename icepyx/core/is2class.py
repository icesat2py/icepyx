import numpy as np
import datetime as dt
import re
import os
import getpass
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
from shapely.geometry.polygon import orient
import matplotlib.pyplot as plt
import fiona
import h5py
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

def _validate_dataset(dataset):
    """
    Confirm a valid ICESat-2 dataset was specified
    """
    if isinstance(dataset, str):
        dataset = str.upper(dataset)
        assert dataset in ['ATL01','ATL02', 'ATL03', 'ATL04','ATL06', 'ATL07', 'ATL08', 'ATL09', 'ATL10', \
                           'ATL12', 'ATL13'],\
        "Please enter a valid dataset"
    else:
        raise TypeError("Please enter a dataset string")
    return dataset
#DevGoal: See if there's a way to dynamically get this list so it's automatically updated

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
    ):

        if dataset is None or spatial_extent is None or date_range is None:
            raise ValueError("Please provide the required inputs. Use help([function]) to view the function's documentation")


        self._dset = _validate_dataset(dataset)

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
                self._spat_extent = self.format_polygon(spatial_extent)
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

        if self.extent_type is 'bounding_box':
            return ['bounding box', self._spat_extent]
        elif self.extent_type is 'polygon':
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
    def granule_info(self):
        """
        Return some basic information about the granules available for the given ICESat-2 data object.

        Examples
        --------
        >>>
        """
        assert len(self.granules)>0, "Your data object has no granules associated with it"
        gran_info = {}
        gran_info.update({'Number of available granules': len(self.granules)})

        gran_sizes = [float(gran['granule_size']) for gran in self.granules]
        gran_info.update({'Average size of granules (MB)': np.mean(gran_sizes)})
        gran_info.update({'Total size of all granules (MB)': sum(gran_sizes)})

        return gran_info


    # ----------------------------------------------------------------------
    # Static Methods

    @staticmethod
    def _fmt_temporal(start,end,key):
        """
        Format the start and end dates and times into a temporal CMR search or subsetting key value.

        Parameters
        ----------
        start : date time object
            Start date and time for the period of interest.
        end : date time object
            End date and time for the period of interest.
        key : string
            Dictionary key, entered as a string, indicating which temporal format is needed.
            Must be one of ['temporal','time'] for data searching and subsetting, respectively.
        """

        assert isinstance(start, dt.datetime)
        assert isinstance(end, dt.datetime)
        #DevGoal: add test for proper keys
        if key is 'temporal':
            fmt_timerange = start.strftime('%Y-%m-%dT%H:%M:%SZ') +',' + end.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif key is 'time':
            fmt_timerange = start.strftime('%Y-%m-%dT%H:%M:%S') +',' + end.strftime('%Y-%m-%dT%H:%M:%S')

        return {key:fmt_timerange}

    @staticmethod
    def _fmt_spatial(ext_type,extent):
        """
        Format the spatial extent input into a spatial CMR search or subsetting key value.

        Parameters
        ----------
        extent_type : string
            Spatial extent type. Must be one of ['bounding_box', 'polygon'] for data searching
            or one of ['bbox, 'bounding_shape'] for subsetting.
        extent : list
            Spatial extent, with input format dependent on the extent type and search.
            Bounding box (bounding_box, bbox) coordinates should be provided in decimal degrees as
            [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
            Polygon (polygon, bounding_shape) coordinates should be provided in decimal degrees as
            [longitude, latitude, longitude2, latitude2... longituden, latituden].
        """

        #CMR keywords: ['bounding_box', 'polygon']
        #subsetting keywords: ['bbox','bounding_shape']
        assert ext_type in ['bounding_box', 'polygon'] or ext_type in ['bbox','bounding_shape'],\
        "Invalid spatial extent type."

        fmt_extent = ','.join(map(str, extent))

        return {ext_type: fmt_extent}

    @staticmethod
    def combine_params(*param_dicts):
        params={}
        for dictionary in param_dicts:
            params.update(dictionary)
        return params



    # ----------------------------------------------------------------------
    # Methods

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



    def format_polygon(self, spatial_extent):
        """
        Formats input spatial file to shapely polygon

        """
        #polygon formatting code borrowed from Amy Steiker's 03_NSIDCDataAccess_Steiker.ipynb demo.
        #DevGoal: use new function geodataframe here?

        gdf = gpd.read_file(spatial_extent)
        #DevGoal: does the below line mandate that only the first polygon will be read? Perhaps we should require files containing only one polygon?
        #RAPHAEL - It only selects the first polygon if there are multiple. Unless we can supply the CMR params with muliple polygon inputs we should probably req a single polygon.
        poly = gdf.iloc[0].geometry
        #Simplify polygon. The larger the tolerance value, the more simplified the polygon. See Bruce Wallin's function to do this
        poly = poly.simplify(0.05, preserve_topology=False)
        poly = orient(poly, sign=1.0)

        #JESSICA - move this into a separate function/CMR formatting piece, since it will need to be used for an input polygon too?
        #Format dictionary to polygon coordinate pairs for CMR polygon filtering
        polygon = (','.join([str(c) for xy in zip(*poly.exterior.coords.xy) for c in xy])).split(",")
        polygon = [float(i) for i in polygon]
        return polygon


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

        if self.extent_type is 'bounding_box':
            boxx = [self._spat_extent[0], self._spat_extent[0], self._spat_extent[2],\
                    self._spat_extent[2], self._spat_extent[0]]
            boxy = [self._spat_extent[1], self._spat_extent[3], self._spat_extent[3],\
                    self._spat_extent[1], self._spat_extent[1]]
            #DevGoal: check to see that the box is actually correctly constructed; have not checked actual location of test coordinates
            gdf = gpd.GeoDataFrame(geometry=[Polygon(list(zip(boxx,boxy)))])
            return gdf
        elif self.extent_type is 'polygon':
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

    def _get_custom_options(self, session):
        """
        Get lists of what customization options are available for the dataset from NSIDC.
        """
        if session is None:
            raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")

        capability_url = f'https://n5eil02u.ecs.nsidc.org/egi/capabilities/{self.dataset}.{self._version}.xml'
        response = session.get(capability_url)
        root = ET.fromstring(response.content)

        # collect lists with each service option
        subagent = [subset_agent.attrib for subset_agent in root.iter('SubsetAgent')]

        # reformatting
        formats = [Format.attrib for Format in root.iter('Format')]
        format_vals = [formats[i]['value'] for i in range(len(formats))]
        format_vals.remove('')

        # reprojection only applicable on ICESat-2 L3B products, yet to be available.

        # reformatting options that support reprojection
        normalproj = [Projections.attrib for Projections in root.iter('Projections')]
        normalproj_vals = []
        normalproj_vals.append(normalproj[0]['normalProj'])
        format_proj = normalproj_vals[0].split(',')
        format_proj.remove('')
        format_proj.append('No reformatting')

        #reprojection options
        projections = [Projection.attrib for Projection in root.iter('Projection')]
        proj_vals = []
        for i in range(len(projections)):
            if (projections[i]['value']) != 'NO_CHANGE' :
                proj_vals.append(projections[i]['value'])

        # reformatting options that do not support reprojection
        no_proj = [i for i in format_vals if i not in format_proj]

        # variable subsetting
        variables = [SubsetVariable.attrib for SubsetVariable in root.iter('SubsetVariable')]
        variables_raw = [variables[i]['value'] for i in range(len(variables))]
        variables_join = [''.join(('/',v)) if v.startswith('/') == False else v for v in variables_raw]
        variable_vals = [v.replace(':', '/') for v in variables_join]

        return [subagent, format_vals, proj_vals, format_proj, no_proj, variable_vals]



    def show_custom_options(self, session):
        """
        Display customization/subsetting options available for this dataset.
        """
        headers=['Subsetting options', 'Data File Formats (Reformatting Options)', 'Reprojection Options',
                 'Data File (Reformatting) Options Supporting Reprojection',
                 'Data File (Reformatting) Options NOT Supporting Reprojection',
                 'Data Variables (also Subsettable)']
        options = self._get_custom_options(session)
        
        for h,o in zip(headers,options):
            print(h)
            pprint.pprint(o)


    def build_CMR_params(self):
        """
        Build a dictionary of CMR parameter keys to submit for granule searches and download.
        """

        if not hasattr(self,'CMRparams'):
            self.CMRparams={}

        CMR_solo_keys = ['short_name','version','temporal']
        CMR_spat_keys = ['bounding_box','polygon']
        #check to see if the parameter list is already built
        if all(keys in self.CMRparams for keys in CMR_solo_keys) and any(keys in self.CMRparams for keys in CMR_spat_keys):
            pass
        #if not, see which fields need to be added and add them
        else:
            for key in CMR_solo_keys:
                if key in self.CMRparams:
                    pass
                else:
                    if key is 'short_name':
                        self.CMRparams.update({key:self.dataset})
                    elif key is 'version':
                        self.CMRparams.update({key:self._version})
                    elif key is 'temporal':
                        self.CMRparams.update(Icesat2Data._fmt_temporal(self._start,self._end,key))
            if any(keys in self.CMRparams for keys in CMR_spat_keys):
                pass
            else:
                self.CMRparams.update(Icesat2Data._fmt_spatial(self.extent_type,self._spat_extent))
                


    #DevGoal: once we've added ability to create a data object from a directory of files, use some of the functionality here to glean the variable list from the file. Otherwise, use self._get_custom_options to build the variable list. Then we don't need to create and maintain and distribute the vardata files at all.
    def build_dataset_vardict(self,filename='',outdir='vardata'):
        '''
        Generate a dictionary contain full paths for variables in the IS2 hdf5 file. 
        This requires: 
                either an existing data file of this dataset 
                or an existing json file containing this data under outdir . 
        By default, these json files are included in the icepyx package under icepyx/vardata
        Parameters:
        -----------
        filename: file name including full path to the existing data file
        outdir: the output directory where json file containing the variable dictionary is. 
        '''

        varlist = []
        vgrp = dict()

        def IS2h5walk(vname, h5node):
            '''
            callable for h5 visititems to return the list of variables
            '''
            if isinstance(h5node, h5py.Dataset):
                varlist.append(vname)
            return 

  
        outdir_abs = os.path.abspath(outdir)     
        fn_vdict = os.path.join(outdir_abs,self.dataset+'.json')

        vgrp = dict()
        if os.path.exists(fn_vdict):
            
            print('Loading variable lists from  file: '+fn_vdict)
            with open(fn_vdict) as fid:
                vgrp   = json.load(fid)
        else:
            
            if not os.path.exists( outdir_abs ): os.makedirs( outdir_abs )   
        
            if os.path.exists(filename):
                
                with h5py.File(filename,'r') as h5pt:
                    h5pt.visititems(IS2h5walk)
                    
                for vn in varlist:
                    vpath,vkey = os.path.split(vn)
                    if vkey not in vgrp.keys():
                        vgrp[vkey] = [vn]
                    else:
                        vgrp[vkey].append(vn)
                        
                with open(fn_vdict,'w') as fid:
                    json.dump(vgrp,fid)

            else:
                raise ValueError("Need an existing data file to generate variable dictionary.")

        
        return vgrp

    #DevGoal: generalize this function to pull info from the _get_custom_options list (rather than requiring the vdatdir input). Then, build the subset parameter within the self.build_subset_params function. If necessary, portions of this can remain as a hidden function to do that formatting, but I suspect we can trim it to only a few lines of code that can go directly into build_subset_params
    def build_subset_coverage(self,vdatdir='vardata',**kwarg):
        '''
        Return the coverage string for data subset request.
        
        Parameters:
        -----------
        vdatdir: local directory of the json file for variable group 
             information of the dataset
        **kwarg: additional keyword arguments:
        beam_ids: the beams to extract for the subset request. For ATL09 use profile_x
        
        return:
        ------ 
        subcover: string of paths of subset variables
        '''
        vdatdir_abs = os.path.abspath(vdatdir)
        vgrpfn = os.path.join(vdatdir_abs,self.dataset+'.json')
        with open(vgrpfn) as fid:
            vgrp   = json.load(fid)
        
        vdict = self.build_subset_vardict(vgrp,**kwarg)
        subcover = ''
        for vn in vdict.keys():
            vpaths = vdict[vn]
            for vpath in vpaths: subcover += '/'+vpath+','
            
        return subcover[:-1]

    #DevGoal: generalize this (and maybe incorporate directly into self.build_subset_params)
    def build_subset_vardict(self,vgrp,**kwarg):
        '''
        Generic wrapper for subsetting variables.
        kwarg: Partly defined in build_subset_coverage, they can also be used for the subsetting of other datasets.
        '''
        if self.dataset=='ATL07': vdict = self._ATL07_vars(vgrp,**kwarg)
        if self.dataset=='ATL09': vdict = self._ATL09_vars(vgrp,**kwarg)
        if self.dataset=='ATL10': vdict = self._ATL10_vars(vgrp,**kwarg)
        return vdict

    #DevGoal: see to what extent we can just have one function that will provide a default list of variables for each dataset (and combine them with any extras from a user defined list). I like the breakdown into kw levels because I think that will help make it more widely applicable across datasets (everyone is likely to want lat and lon).
    def _ATL09_vars(self,vgrp,
                    kw1_list=['profile_1','profile_2','profile_3','orbit_info'],
                    kw2_list = ['high_rate','low_rate','bckgrd_atlas'],
                    var_list = None,
                    add_default_vars=True):
        '''
        Build the variable dictionary using user specified beams and variable list. 
        A pregenerated default variable list can be used by setting add_default_vars to True. 
        Note: The calibrated backscatter cab_prof is not in the default list
        Parameters:
        -----------
        kw1_list:         a list of first level tag in the full path of the variable.
                          For ATL09, this include: profile_x's and orbit_info
                          ancillary_data and quality_assessment variables will be added 
                          because of their negligible size. 
        var_list:         a list of variables to include for subsetting. 
                          If var_list is not provided, a default list will be used. 
        kw2_list:         a list of second level tag in the full path of the variable. 
                          For ATL09, this is valid only if kw1 is profile_x's and may include
                          high_rate, low_rate, bckgrd_atlas 
        add_default_vars: The flag to append the variables in the default list to the user defined list. 
                          It is set to True by default. 
        '''

        vd09 = dict({})

        def_varlist = ['delta_time','latitude','longitude',
                       'bsnow_h','bsnow_dens','bsnow_con','bsnow_psc','bsnow_od',
                       'cloud_flag_asr','cloud_fold_flag','cloud_flag_atm',
                       'column_od_asr','column_od_asr_qf',
                       'layer_attr','layer_bot','layer_top','layer_flag','layer_dens','layer_ib',
                       'msw_flag','prof_dist_x','prof_dist_y','apparent_surf_reflec']
        
        if var_list is not None:
            if add_default_vars:
                for vn in def_varlist:
                    if vn not in var_list: var_list.append(vn)
        else:
            var_list = def_varlist

        for vkey in vgrp:
            vpaths = vgrp[vkey]
            
            for vpath in vpaths:
                
                vpath_kws = vpath.split('/')
                if vpath_kws[0] in ['quality_assessment','ancillary_data']:
                    if vkey not in vd09: vd09[vkey] = []
                    vd09[vkey].append(vpath)     
                elif vpath_kws[0]=='orbit_info':
                    if vkey not in vd09: vd09[vkey] = []
                    if vpath_kws[-1] in var_list:
                        vd09[vkey].append(vpath)
                elif vpath_kws[0] in kw1_list and \
                    vpath_kws[1] in kw2_list and \
                    vpath_kws[-1] in var_list:
                    if vkey not in vd09: vd09[vkey] = []
                    vd09[vkey].append(vpath)
                        
        return vd09
    
    #DevGoal: this may need some additional args depending on the above...
    def build_subset_params(self, **kwargs):
        """
        Build a dictionary of subsetting parameter keys to submit for data orders and download.
        """

        if not hasattr(self,'subsetparams'):
            self.subsetparams={}

        #DevGoal: get list of available subsetting options for the dataset and use this to build appropriate subset parameters
        default_keys = ['time']
        spat_keys = ['bbox','bounding_shape']
        opt_keys = ['format','projection','projection_parameters','Coverage']
        #check to see if the parameter list is already built
        if all(keys in self.subsetparams for keys in default_keys) and (any(keys in self.subsetparams for keys in spat_keys) or hasattr(self, '_geom_filepath')):
            pass
        #if not, see which fields need to be added and add them
        else:
            for key in default_keys:
                if key in self.subsetparams:
                    pass
                else:
                    if key is 'time':
                        self.subsetparams.update(Icesat2Data._fmt_temporal(self._start,self._end, key))
            if any(keys in self.subsetparams for keys in spat_keys) or hasattr(self, '_geom_filepath'):
                pass
            else:
                if self.extent_type is 'bounding_box':
                    k = 'bbox'
                elif self.extent_type is 'polygon':
                    k = 'bounding_shape'
                self.subsetparams.update(Icesat2Data._fmt_spatial(k,self._spat_extent))
            for key in opt_keys:
                if key in kwargs:
                    self.subsetparams.update({key:kwargs[key]})
                else:
                    pass


    def build_reqconfig_params(self,reqtype, **kwargs):
        """
        Build a dictionary of request configuration parameters.
        #DevGoal: Allow updating of the request configuration parameters (right now they must be manually deleted to be modified)
        """

        if not hasattr(self,'reqparams') or self.reqparams==None:
            self.reqparams={}

        if reqtype is 'search':
            reqkeys = ['page_size','page_num']
        elif reqtype is 'download':
            reqkeys = ['page_size','page_num','request_mode','token','email','include_meta']
        else:
            raise ValueError("Invalid request type")

        if all(keys in self.reqparams for keys in reqkeys):
            pass
        else:
            defaults={'page_size':10,'page_num':1,'request_mode':'async','include_meta':'Y'}
            for key in reqkeys:
                if key in kwargs:
                    self.reqparams.update({key:kwargs[key]})
#                 elif key in defaults:
#                     if key is 'page_num':
#                         pnum = math.ceil(len(self.granules)/self.reqparams['page_size'])
#                         if pnum > 0:
#                             self.reqparams.update({key:pnum})
#                         else:
#                             self.reqparams.update({key:defaults[key]})
                elif key in defaults:
                    self.reqparams.update({key:defaults[key]})
                else:
                    pass

        #DevGoal: improve the interfacing with NSIDC/DAAC so it's not paging results
        self.reqparams['page_num'] = 1


    def avail_granules(self):
        """
        Get a list of available granules for the ICESat-2 data object's parameters
        """

        granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'

        self.granules = []
        self.build_CMR_params()
        self.build_reqconfig_params('search')
        headers={'Accept': 'application/json'}
        #DevGoal: check the below request/response for errors and show them if they're there; then gather the results
        #note we should also do this whenever we ping NSIDC-API - make a function to check for errors
        while True:
            response = requests.get(granule_search_url, headers=headers,\
                                    params=self.combine_params(self.CMRparams,\
                                                               {k: self.reqparams[k] for k in ('page_size','page_num')}))

            results = json.loads(response.content)
            print(results)
            if len(results['feed']['entry']) == 0:
                # Out of results, so break out of loop
                break

            # Collect results and increment page_num
            self.granules.extend(results['feed']['entry'])
            self.reqparams['page_num'] += 1

        assert len(self.granules)>0, "Your search returned no results; try different search parameters"

        return self.granule_info


    def earthdata_login(self,uid,email):
        """
        Initiate an Earthdata session and create a token for interacting
        with the NSIDC DAAC. This function will prompt the user for
        their Earthdata password, but will only store that information
        within the active session.

        Parameters
        ----------
        uid : string
            Earthdata Login user name.
        email : string
            Complete email address, provided as a string.

        Examples
        --------
        >>> region_a = [define that here]
        >>> region_a.earthdata_login('sam.smith','sam.smith@domain.com')
        Earthdata Login password:  ········
        """

        if not hasattr(self,'reqparams'):
            self.reqparams={}

        assert isinstance(uid, str), "Enter your login user id as a string"
        assert re.match(r'[^@]+@[^@]+\.[^@]+',email), "Enter a properly formatted email address"

        pswd = getpass.getpass('Earthdata Login password: ')

        #Request CMR token using Earthdata credentials
        token_api_url = 'https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens'
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        data = {'token': {'username': uid, 'password': pswd,\
                          'client_id': 'NSIDC_client_id','user_ip_address': ip}
        }
        
        response = requests.post(token_api_url, json=data, headers={'Accept': 'application/json'})
        
        #check for a valid login and retry up to 5 times if errors were returned
        for i in range(5):
            try:
                json.loads(response.content)['token']
                break
            except KeyError:
                try:
                    print(json.loads(response.content)['errors'])
                    uid = input("Please re-enter your Earthdata user ID: ")
                    pswd = getpass.getpass('Earthdata Login password: ')
                    data = {'token': {'username': uid, 'password': pswd,\
                          'client_id': 'NSIDC_client_id','user_ip_address': ip}
                            }
                    response = None
                    response = requests.post(token_api_url, json=data, headers={'Accept': 'application/json'})
                    i = i+1

                except KeyError:
                    print("There are no error messages, but an Earthdata login token was not successfully generated")
        else:
            raise RuntimeError("You could not successfully obtain an Earthdata login token")
            
        token = json.loads(response.content)['token']['id']

        self.reqparams.update({'email': email, 'token': token})

        #Start a session
        capability_url = f'https://n5eil02u.ecs.nsidc.org/egi/capabilities/{self.dataset}.{self._version}.xml'
        session = requests.session()
        s = session.get(capability_url)
        response = session.get(s.url,auth=(uid,pswd))

        return session

    #DevGoal: display output to indicate number of granules successfully ordered (and number of errors)
    def order_granules(self, session, verbose=False, subset=True, **kwargs):
        """
        Place an order for the available granules for the ICESat-2 data object.
        Adds the list of zipped files (orders) to the data object.
        DevGoal: add additional kwargs to allow subsetting and more control over request options.
        Note: This currently uses paging to download data - this may not be the best method

        Parameters
        ----------
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object can be obtained using is2_data.earthdata_login(uid, email) and entering your
            Earthdata login password when prompted. You must have previously registered for an Earthdata account.

        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.

        subset : boolean, default True
            Use input temporal and spatial search parameters to subset each granule and return only data
            that is actually within those parameters (rather than complete granules which may contain only
            a small area of interest).

        kwargs...
        """

        if session is None:
            raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")

        base_url = 'https://n5eil02u.ecs.nsidc.org/egi/request'
        #DevGoal: get the base_url from the granules

        self.build_CMR_params()
        self.build_reqconfig_params('download')

        if subset is False:
            request_params = self.combine_params(self.CMRparams, self.reqparams, {'agent':'NO'})
        else:
#             if kwargs is None:
#                 #make subset params and add them to request params
#                 self.build_subset_params()
#                 request_params = self.combine_params(self.CMRparams, self.reqparams, self.subsetparams)
#             else:
#                 #make subset params using kwargs and add them to request params
#                 self.build_subset_params(kwargs)
#                 request_params = self.combine_params(self.CMRparams, self.reqparams, self.subsetparams)
            self.build_subset_params(**kwargs)
            request_params = self.combine_params(self.CMRparams, self.reqparams, self.subsetparams)

        granules=self.avail_granules() #this way the reqparams['page_num'] is updated

        # Request data service for each page number, and unzip outputs
        for i in range(request_params['page_num']):
            page_val = i + 1
            if verbose is True:
                print('Order: ', page_val)
            request_params.update( {'page_num': page_val} )

        # For all requests other than spatial file upload, use get function
        #add line here for using post instead of get with polygon and subset
        #also, make sure to use the full polygon, not the simplified one used for finding granules
            if subset is True and hasattr(self, '_geom_filepath'):
                #post polygon file to OGR for geojson conversion
                #DevGoal: what is this doing under the hood, and can we do it locally?

                request = session.post(base_url, params=request_params, \
                                       files={'shapefile': open(str(self._geom_filepath), 'rb')})
            else:
                request = session.get(base_url, params=request_params)
            
            root=ET.fromstring(request.content)
            print([subset_agent.attrib for subset_agent in root.iter('SubsetAgent')])

            if verbose is True:
                print('Request HTTP response: ', request.status_code)
                print('Order request URL: ', request.url)

        # Raise bad request: Loop will stop for bad response code.
            request.raise_for_status()
            esir_root = ET.fromstring(request.content)
            if verbose is True:
                print('Order request URL: ', request.url)
                print('Order request response XML content: ', request.content)

        #Look up order ID
            orderlist = []
            for order in esir_root.findall("./order/"):
                if verbose is True:
                    print(order)
                orderlist.append(order.text)
            orderID = orderlist[0]
            print('order ID: ', orderID)

        #Create status URL
            statusURL = base_url + '/' + orderID
            if verbose is True:
                print('status URL: ', statusURL)

        #Find order status
            request_response = session.get(statusURL)
            if verbose is True:
                print('HTTP response from order response URL: ', request_response.status_code)

        # Raise bad request: Loop will stop for bad response code.
            request_response.raise_for_status()
            request_root = ET.fromstring(request_response.content)
            statuslist = []
            for status in request_root.findall("./requestStatus/"):
                statuslist.append(status.text)
            status = statuslist[0]
            print('Data request ', page_val, ' is submitting...')
            print('Initial request status is ', status)

        #Continue loop while request is still processing
            while status == 'pending' or status == 'processing':
                print('Status is not complete. Trying again.')
                time.sleep(10)
                loop_response = session.get(statusURL)

        # Raise bad request: Loop will stop for bad response code.
                loop_response.raise_for_status()
                loop_root = ET.fromstring(loop_response.content)

        #find status
                statuslist = []
                for status in loop_root.findall("./requestStatus/"):
                    statuslist.append(status.text)
                status = statuslist[0]
                print('Retry request status is: ', status)
                if status == 'pending' or status == 'processing':
                    continue

        #Order can either complete, complete_with_errors, or fail:
        # Provide complete_with_errors error message:
            if status == 'complete_with_errors' or status == 'failed':
                messagelist = []
                for message in loop_root.findall("./processInfo/"):
                    messagelist.append(message.text)
                print('error messages:')
                pprint.pprint(messagelist)

            if status == 'complete' or status == 'complete_with_errors':
                if not hasattr(self,'orderIDs'):
                    self.orderIDs=[]

                self.orderIDs.append(orderID)
            else: print('Request failed.')



    def download_granules(self, session, path, verbose=False): #, extract=False):
        """
        Downloads the data ordered using order_granules.

        Parameters
        ----------
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object can be obtained using is2_data.earthdata_login(uid, email) and entering your
            Earthdata login password when prompted. You must have previously registered for an Earthdata account.
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

        #Note: need to test these checks still
        if session is None:
            raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")
            #DevGoal: make this a more robust check for an active session

        if not hasattr(self,'orderIDs') or len(self.orderIDs)==0:
            try:
                self.order_granules(session, verbose=verbose)
            except:
                if not hasattr(self,'orderIDs') or len(self.orderIDs)==0:
                    raise ValueError('Please confirm that you have submitted a valid order and it has successfully completed.')

        if not os.path.exists(path):
            os.mkdir(path)

        os.chdir(path)

        for order in self.orderIDs:
            downloadURL = 'https://n5eil02u.ecs.nsidc.org/esir/' + order + '.zip'
            #DevGoal: get the download_url from the granules

            if verbose is True:
                print('Zip download URL: ', downloadURL)
            print('Beginning download of zipped output...')
            zip_response = session.get(downloadURL)
            # Raise bad request: Loop will stop for bad response code.
            zip_response.raise_for_status()
            print('Data request', order, 'of ', len(self.orderIDs), ' order(s) is complete.')

#         #Note: extract the dataset to save it locally
#         if extract is True:
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                z.extractall(path)
