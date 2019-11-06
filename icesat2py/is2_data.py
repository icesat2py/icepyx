#import numpy as np
import datetime as dt
import re
import getpass
import socket
import requests
import json
import warnings


def validate_dataset(dataset):
    """
    Confirm a valid ICESat-2 dataset was specified
    """
    if isinstance(dataset, str):
        dataset = str.upper(dataset)
        assert dataset in ['ATL01','ATL02', 'ATL03', 'ATL04','ATL06', 'ATL07', 'ATL08', 'ATL09', 'ATL10', \
                           'ATL12', 'ATL13'],\
        "Please enter a valid dataset"
    else:
        raise ValueError("Please enter a dataset string")
    return dataset
#DevQuestion: since this function is validating an entry, does it also make sense to have a test for it?
#DevGoal: See if there's a way to dynamically get this list so it's automatically updated


class Icesat2Data():
    """
    ICESat-2 Data object to query, obtain, and perform basic operations on 
    available ICESat-2 datasets using temporal and spatial input parameters. 
    Allows the easy input and formatting of search parameters to match the 
    NASA NSIDC DAAC and conversion to multiple data types.
    
    Parameters
    ----------
    dataset : string
        ICESat-2 dataset ID, also known as "short name" (e.g. ATL03). 
        Available datasets can be found at: https://nsidc.org/data/icesat-2/data-sets
    spatial_extent : list
        Spatial extent of interest, provided as a bounding box. 
        Bounding box coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        DevGoal: allow broader input of polygons and polygon files (e.g. kml, shp) as bounding areas
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

            
        self.dset = validate_dataset(dataset)
         
        if isinstance(spatial_extent, list):
            if len(spatial_extent)==4:
                #BestPractices: move these assertions to a more general set of tests for valid geometries?
                assert -90 <= spatial_extent[1] <= 90, "Invalid latitude value"
                assert -90 <= spatial_extent[3] <= 90, "Invalid latitude value"
                assert -180 <= spatial_extent[0] <= 360, "Invalid longitude value" #tighten these ranges depending on actual allowed inputs
                assert -180 <= spatial_extent[2] <= 360, "Invalid longitude value"
                assert spatial_extent[0] <= spatial_extent[2], "Invalid bounding box longitudes"
                assert spatial_extent[1] <= spatial_extent[3], "Invalid bounding box latitudes"
                self.spat_extent = spatial_extent
                self.extent_type = 'bounding_box'
            else:
                raise ValueError('Your spatial extent bounding box needs to have four entries')
                           
            
        if isinstance(date_range, list):
            if len(date_range)==2:
                self.start = dt.datetime.strptime(date_range[0], '%Y-%m-%d')
                self.end = dt.datetime.strptime(date_range[1], '%Y-%m-%d')
                #BestPractices: can the check that it's a valid date entry be implicit (e.g. by converting it to a datetime object, as done here?) or must it be more explicit?
                assert self.start.date() <= self.end.date(), "Your date range is invalid"               
            else:
                raise ValueError("Your date range list is the wrong length. It should have start and end dates only.")
            
#         elif isinstance(date_range, date-time object):
#             print('it is a date-time object')
#         elif isinstance(date_range, dict):
#             print('it is a dictionary. now check the keys for start and end dates')
                        
        
        if start_time is None:
            self.start = self.start.combine(self.start.date(),dt.datetime.strptime('00:00:00', '%H:%M:%S').time())
        else:
            if isinstance(start_time, str):
                self.start = self.start.combine(self.start.date(),dt.datetime.strptime(start_time, '%H:%M:%S').time())
            else:
                raise ValueError("Please enter your start time as a string")
        
        if end_time is None:
            self.end = self.start.combine(self.end.date(),dt.datetime.strptime('23:59:59', '%H:%M:%S').time())
        else:
            if isinstance(end_time, str):
                self.end = self.start.combine(self.end.date(),dt.datetime.strptime(end_time, '%H:%M:%S').time())
            else:
                raise ValueError("Please enter your end time as a string")
                
        latest_vers = self.latest_version()
        if version is None:
            self.version = latest_vers
        else:
            if isinstance(version, str):
                assert int(version)>0, "Version number must be positive"
                vers_length = 3
                self.version = version.zfill(vers_length)
            else:
                raise ValueError("Please enter the version number as a string")
            
            if int(self.version) < int(latest_vers):
                warnings.filterwarnings("always")
                warnings.warn("You are using an old version of this dataset")

        self.params={}
    
    # ----------------------------------------------------------------------
    # Properties
    
    @property
    def dataset(self):
        """
        Return the short name dataset ID string associated with the ICESat-2 data object.
        
        Example
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.dataset
        ATL06
        """
        return self.dset
    
    @property
    def spatial_extent(self):
        """
        Return an array showing the spatial extent of the ICESat-2 data object.
        Spatial extent is returned as an input type followed by the geometry data.
        Bounding box data is [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.spatial_extent
        ['bounding box', [-64, 66, -55, 72]]
        """
        
        if self.extent_type is 'bounding_box':
            return ['bounding box', self.spat_extent]
        else:
            return ['unknown spatial type', self.spat_extent]
         
        
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
        return [self.start.strftime('%Y-%m-%d'), self.end.strftime('%Y-%m-%d')] #could also use self.start.date()
    
    
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
        return self.start.strftime('%H:%M:%S')

    @property
    def end_time(self):
        """
        Return the end time specified for the end date.
        
        Example
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.end_time
        23:59:59
        
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], end_time='10:20:20')
        >>> region_a.end_time
        10:20:20
        """
        return self.end.strftime('%H:%M:%S')
    
    @property
    def dataset_version(self):
        """
        Return the dataset version of the data object.
        
        Example
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> region_a.dataset_version
        002
        
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'], version='1')
        >>> region_a.dataset_version
        001
        """
        return self.version

    #Note: Would it be helpful to also have start and end properties that give the start/end date+time?
    
    # ----------------------------------------------------------------------
    # Static Methods

    @staticmethod
    def earthdata_login(uid,email):
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

        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.earthdata_login('sam.smith','sam.smith@domain.com')
        Earthdata Login password:  ········
        """

        assert isinstance(uid, str), "Enter your login user id as a string"
        assert re.match(r'[^@]+@[^@]+\.[^@]+',email), "Enter a properly formatted email address"
        
        pswd = getpass.getpass('Earthdata Login password: ')
        
    @staticmethod
    def cmr_fmt_temporal(start,end):
        """
        Format the start and end dates and times into a temporal CMR search key.
        
        Parameters
        ----------
        start : date time object
            Start date and time for the period of interest.
        end : date time object
            End date and time for the period of interest.
        """
        
        assert isinstance(start, dt.datetime)
        assert isinstance(end, dt.datetime)
        fmt_timerange = [start.strftime('%Y-%m-%dT%H:%M:%SZ'),end.strftime('%Y-%m-%dT%H:%M:%S')]
        
        return {'temporal':fmt_timerange}
        
    @staticmethod
    def cmr_fmt_spatial(ext_type,extent):
        """
        Format the spatial extent input into a spatial CMR search key.
        
        Parameters
        ----------
        extent_type : string
            Spatial extent type. Must be one of ['bounding_box'].
        extent : list
            Spatial extent, with input format dependent on the extent type.
            Bounding box coordinates should be provided in decimal degrees as
            [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        """
        
        assert ext_type in ['bounding_box'], "Invalid spatial extent type."
        
        if ext_type=='bounding_box':
            fmt_extent = ','.join(map(str, extent))
             
        return {ext_type: fmt_extent}
        
        

    # ----------------------------------------------------------------------
    # Methods

    def about_dataset(self): 
        """
        Return metadata about the dataset of interest (the collection).
        """
        
        cmr_collections_url = 'https://cmr.earthdata.nasa.gov/search/collections.json'
        response = requests.get(cmr_collections_url, params={'short_name': self.dset})
        results = json.loads(response.content)
        return results
        #DevGoal: provide a more readable data format if the user prints the data (look into pprint, per Amy's tutorial)
    
    def latest_version(self):
        """
        Determine the most recent version available for the given dataset.
        """
        dset_info = self.about_dataset()
        return max([entry['version_id'] for entry in dset_info['feed']['entry']])
        
    def build_CMR_params(self):
        """
        Build a dictionary of CMR parameter keys to submit for granule searches and download.
        """
        
        CMR_solo_keys = ['short_name','version','temporal','page_size','page_num']
        CMR_spat_keys = ['bounding_box','polygon']
        #check to see if the parameter list is already built
        if all(keys in self.params for keys in CMR_solo_keys) and any(keys in self.params for keys in CMR_spat_keys):
            pass
        #if not, see which fields need to be added and add them
        else:
            for key in CMR_solo_keys:
                if key in self.params:
                    pass
                else:
                    if key is 'short_name':
                        self.params.update({key:self.dataset})    
                    elif key=='version':
                        self.params.update({key:self.version})
                    elif key=='temporal':
                        self.params.update({key:self.cmr_fmt_temporal(self.start,self.end)})
                    elif key=='page_size':
                        self.params.update({key:100})
                    elif key=='page_num':
                         self.params.update({key:1})
            if any(keys in self.params for keys in CMR_spat_keys):
                pass
            else:
                self.params.update(self.cmr_fmt_spatial(self.extent_type,self.spat_extent))
        
#         return self.params
    
    
#     def avail_granules(self):
#         """
#         Get a list of available granules for the ICESat-2 data object's parameters
#         """
        
#         granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'

#         self.granules = []
#         while True:
#             response = requests.get(granule_search_url, params=self.build_CMR_params(), headers=self.headers)
#             results = json.loads(response.content)

#             if len(results['feed']['entry']) == 0:
#                 # Out of results, so break out of loop
#                 break

#             # Collect results and increment page_num
#             self.granules.extend(results['feed']['entry'])
#             self.params['page_num'] += 1
                    
# #         return self.granules
        

        
        
    



