#import numpy as np
import datetime as dt
import re

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
    spatial_extent : ndarray
        Spatial extent of interest, provided as a bounding box or single, closed
        polygon geometry. Bounding box coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        DevGoal: allow broader input of polygons and polygon files (e.g. kml, shp) as bounding areas
    date_range : list of 'YYYY-MM-DD' strings
        Date range of interest, provided as start and end dates, inclusive.
        The required date format is 'YYYY-MM-DD' strings, where
        YYYY = 4 digit year, MM = 2 digit month, DD = 2 digit day.
        Currently, a list of specific dates (rather than a range) is not accepted.
        DevGoal: accept date-time objects, dicts (with 'start_date' and 'end_date' keys, and DOY inputs.
        DevGoal: allow searches with a list of dates, rather than a range.
    start_time : HH:mm:ss, default 00:00:00
        Start time in UTC/Zulu. If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    end_time : HH:mm:ss, default 23:59:59
        End time in UTC/Zulu. If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    version : string, default most recent version
        Dataset version, given as a 3 digit string. If no version is given, the current
        version is used.
        Current version (Oct 2019): 001
    
        
    See Also
    --------


    Examples
    --------
    Initializing Icesat2Data with a bounding box.
    >>> sho
    >>> reg_a_bbox = [lllong, lllat, urlong, urlat]
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
#         spatial_extent = None,
        date_range = None,
        start_time = None,
#         end_time = None,
#         version = None,
    ):
        
        if dataset is None or date_range is None:
            raise ValueError("Please provide the required inputs. Use help([function]) to view the function's documentation")

            
        if isinstance(dataset, str):
            self.dset = str.upper(dataset)
            assert self.dset in ['ATL02', 'ATL03', 'ATL04','ATL06', 'ATL07', 'ATL08', 'ATL09', 'ATL10', 'ATL12', 'ATL13'],\
            "Please enter a valid dataset"
        else:
            raise ValueError("Please enter a dataset string")
                    
            
        if isinstance(date_range, list):
            if len(date_range)==2:
                self.start = dt.datetime.strptime(date_range[0], '%Y-%m-%d')
                self.end = dt.datetime.strptime(date_range[1], '%Y-%m-%d')
                #BestPractices: can the check that it's a valid date entry be implicit (e.g. by converting it to a datetime object, as done here?) or must it be more explicit?
                               
            else:
                raise ValueError("Your date range list is the wrong length. It should have start and end dates only.")
            
#         elif istype(date_range, date-time object):
#             print('it is a date-time object')
#         elif isinstance(date_range, dict):
#             print('it is a dictionary. now check the keys for start and end dates')
        

#         self.date_range = format_dates(start_date, end_date)
#         when writing the format dates/times function, check with an assertion that the start date is before the end date
                
        
        if start_time is None:
            self.start = dt.datetime.strptime('00:00:00', '%H:%M:%S')
        else:
            if isinstance(start_time, str):
                self.start = dt.datetime.strptime(start_time, '%H:%M:%S')
            else:
                raise ValueError("Please enter your start time as a string")
        
    
    # ----------------------------------------------------------------------
    # Properties
    
    @property
    def dataset(self):
        """
        Return the short name dataset ID string associated with the ICESat-2 data object.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.dataset
        [put output here]
        """
        return self.dset
    
    @property
    def dates(self):
        """
        Return an array showing the date range of the ICESat-2 data object.
        Dates are returned as an array containing the start and end datetime objects, inclusive, in that order.

        Examples
        --------
        >>> region_a = [define that here]
        >>> region_a.dates
        [put output here]
        """
        return [self.start.strftime('%Y-%m-%d'), self.end.strftime('%Y-%m-%d')]
    
    
    @property
    def start_time(self):
        """
        Return the start time specified for the start date.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.dataset
        [put output here]
        """
        return self.start.strftime('%H:%M:%S')

    # ----------------------------------------------------------------------
    # Static Methods

#     @staticmethod
#     def time_range_params(time_range): #initial version copied from topohack; ultimately will be modified heavily
#         """
#         Construct 'temporal' parameter for API call.

#         :param time_range: dictionary with specific time range
#                            *Required_keys* - 'start_date', 'end_date'
#                            *Format* - 'yyyy-mm-dd'

#         :return: Time string for request parameter or None if required keys are
#                  missing.
#         """
#         start_time = '00:00:00'  # Start time in HH:mm:ss format
#         end_time = '23:59:59'    # End time in HH:mm:ss format

#         if 'start_date' not in time_range or 'end_date' not in time_range:
#             return None

#         return f"{time_range['start_date']}T{start_time}Z," \
#             f"{time_range['end_date']}T{end_time}Z"