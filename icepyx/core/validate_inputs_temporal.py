import datetime as dt
import os
import warnings
import geopandas as gpd
import numpy as np

import icepyx.core.APIformatting as apifmt
import icepyx.core.geospatial as geospatial

'''
Helper functions for validation of dates

'''


def check_valid_date_range(start, end):

    """
    Helper function for checking date ranges
    An AssertionError is raised if the start date is later than the end date.

    Parameters
    ----------
    start: datetime object containing a start date
    end: datetime object containing an end date

    Returns
    -------
    boolean (true if date range is valid, false otherwise)

    """

    assert start.date() <= end.date(), "Your date range is invalid"


def make_datetime(start_date, end_date, start_time, end_time):

    """
    Helper function for creating combined datetime objects
    out of start/end dates and their respective start/end times

    Parameters
    ----------
    start_date, end_date: datetime objects that only contain date
    start_time, end_time: datetime objects that only contain time

    Returns
    -------
    start_datetime: start datetime object, combination of start_date + start_time
    end_datetime: end datetime object, combination of end_date +  end_time

    """

    _start_datetime = dt.datetime.combine(
        start_date.date(), start_time.time()
    )
    _end_datetime = dt.datetime.combine(
        end_date.date(), end_time.time()
    )
    return _start_datetime, _end_datetime


def validate_date_range_datestr(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of strings (list must be of length 2).
    Strings must be of format: "YYYY-MM-DD" (Otherwise, datetime.strptime() will throw ValueError)

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """

    _start = dt.datetime.strptime(date_range[0], "%Y-%m-%d")
    _end = dt.datetime.strptime(date_range[1], "%Y-%m-%d")

    check_valid_date_range(_start, _end)

    _start, _end = make_datetime(_start, _end, start_time, end_time)

    return _start, _end


def validate_date_range_datetime(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of datetime objects (list must be of length 2).

    NOTE: if start_time OR end_time are not none, throw a warning! These will be ignored
    in favor of the times inside of the date_range datetime objects.

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """

    check_valid_date_range(date_range[0], date_range[1])

    _start, _end = make_datetime(date_range[0].date(), date_range[1].date(), date_range[0].time(), date_range[1].time())

    return _start, _end


def validate_date_range_date(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of Date objects (list must be of length 2).

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """

    check_valid_date_range(date_range[0], date_range[1])

    _start, _end = make_datetime(date_range[0], date_range[1], start_time, end_time)

    return _start, _end


def validate_date_range_dict(date_range, start_time, end_time):

    """
     Validates a date RANGE provided in the form of a dict with the following keys:
         start_date: start date, type can be of dt.datetime, dt.date, or string
         end_date: end date, type can be of dt.datetime, dt.date, or string

      NOTE: The keys MUST have the exact names/formatting above or a ValueError will be thrown by this function.
      NOTE: If the keys are of type dt.datetime, the start_time/end_time parameters will be ignored!

     Returns the start and end datetimes as datetime objects
     by combining the start/end dates with their respective start/end times.

     """

    _start_date = date_range.get("start_date")
    _end_date = date_range.get("end_date")

    if _start_date is None or _end_date is None:
        raise ValueError("Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

    # start_date
    #   if is datetime
    if isinstance(_start_date, dt.datetime):
        # Ignore start/end times, return raw start date
        if start_time is not None:
            warnings.warn("Warning: \"start_date\" given as datetime, but start_time argument was provided. \n"
                          "This argument will be ignored and the time from the start_date datetime object"
                          " will be used as start times.")
    # if is only date
    elif isinstance(_start_date, dt.date):
        _start_date = dt.datetime.combine(
            _start_date, start_time.time()
        )

    # if is string date
    elif isinstance(_start_date, str):
        _start_date = dt.datetime.strptime(_start_date, "%Y-%m-%d")

    #   else; raise valueerror, some invalid type
    else:
        raise ValueError("Invalid type for key 'start_date'.\n"
                         "Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

    if end_time is not None:
        warnings.warn("Warning: \"end_date\" given as datetime, but end_time argument was provided. \n"
                      "This argument will be ignored and the time from the end_date datetime object"
                      " will be used as end times.")

    # ######################### end_date #######################################
    # if is datetime

    if isinstance(_end_date, dt.datetime):
        # Ignore start/end times, return raw start date
        if end_time is not None:
            warnings.warn("Warning: \"end_date\" given as datetime, but end_time argument was provided. \n"
                          "This argument will be ignored and the time from the end_date datetime object"
                          " will be used as end times.")
        # if is only date
    elif isinstance(_end_date, dt.date):
        _end_date = dt.datetime.combine(
            _end_date, end_time.time()
        )

        # if is string date
    elif isinstance(_end_date, str):
        _end_date = dt.datetime.strptime(_end_date, "%Y-%m-%d")

        #   else; raise valueerror, some invalid type
    else:
        raise ValueError("Invalid type for key 'end_date'.\n"
                         "Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

    return _start_date, _end_date


def validate_date_list_datestr(date_range, start_time, end_time):


    """
     Validates a LIST OF DATES provided in the form of a list of strings.
     Strings must be of format: "YYYY-MM-DD" (Otherwise, datetime.strptime() will throw ValueError)

     Returns the datetimes as datetime objects
     by combining the start/end dates with their respective start/end times.

     """

    _start = dt.datetime.strptime(date_range[0], "%Y-%m-%d")
    _end = dt.datetime.strptime(date_range[1], "%Y-%m-%d")

    check_valid_date_range(_start, _end)

    _start, _end = make_datetime(_start, _end, start_time, end_time)

    return _start, _end

def validate_date_list_datetime(date_range, start_time, end_time):

    return 0, 0


def validate_date_list_date(date_range, start_time, end_time):

    return 0, 0


'''
 date_range : list of 'YYYY-MM-DD' strings
        Date range of interest, provided as start and end dates, inclusive.
        The required date format is 'YYYY-MM-DD' strings, where
        YYYY = 4 digit year, MM = 2 digit month, DD = 2 digit day.
        Currently, a list of specific dates (rather than a range) is not accepted.
        TODO: accept date-time objects, dicts (with 'start_date' and 'end_date' keys), and DOY inputs.
        TODO: allow searches with a list of dates, rather than a range.
    start_time : HH:mm:ss, default 00:00:00
        Start time in UTC/Zulu (24 hour clock). If None, use default.
        TODO: check for time in date-range date-time object, if that's used for input.
    end_time : HH:mm:ss, default 23:59:59
        End time in UTC/Zulu (24 hour clock). If None, use default.
        TODO: check for time in date-range date-time object, if that's used for input.
'''


class Temporal:
    def __init__(self, date_range, start_time=None, end_time=None):

        valid_time_types = (str, dt.time)

        # Validate start/end time types; then convert them to the appropriate datetime object

        if start_time is not None:
            # user specified a start time, need to first check if it's a valid type (if not, throw an AssertionError)
            assert isinstance(start_time, valid_time_types), "start_time must be one of the following types: \n" \
                                                             "str (format: HH:MM:SS)\n" \
                                                             "datetime.time"
            # if start_time is a string, then it must be converted to a datetime using strptime
            if not isinstance(start_time, dt.time):
                start_time = dt.datetime.strptime(start_time, "%H:%M:%S")
        else:
            # if user did not specify a start time, default to start time of 00:00:00
            start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S")

        if end_time is not None:
            # user specified an end time, need to first check if it's a valid type (if not, throw an AssertionError)
            assert isinstance(end_time, valid_time_types), "end_time must be one of the following types: \n" \
                                                             "str (format: HH:MM:SS)\n" \
                                                             "datetime.time"
            # if end_time is a string, then it must be converted to a datetime using strptime
            if not isinstance(end_time, dt.time):
                end_time = dt.datetime.strptime(end_time, "%H:%M:%S")

        else:
            # if user did not specify an end time, default to end time of 23:59:59
            end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S")

        if len(date_range) == 2:
            # range, list of dates
            # can be date objects, dicts, datetime objects, DOY input (YYYY-DOY)

            if all(isinstance(i, str) for i in date_range):
                self._datelist, self._isrange = validate_date_range_datestr(date_range, start_time, end_time)
            elif all(isinstance(i, dt.datetime) for i in date_range):
                # TODO: Throw a warning if start_time/end_time are not "None" and use dt object
                self._starttime, self._isrange = validate_date_range_datetime(date_range, start_time, end_time)
            elif all(isinstance(i, dt.date) for i in date_range):
                self._starttime,  self._isrange = validate_date_range_date(date_range, start_time, end_time)
            elif all(isinstance(i, dict) for i in date_range):
                self._starttime,  self._isrange = validate_date_range_dict(date_range, start_time, end_time)
            else:
                # input type is invalid
                # TODO: Flesh out this TypeError once this class is done
                raise TypeError("date_range must be a list of one of the following: \n")

        else:
            # assume list of dates (1, or 3 or more)
            if all(isinstance(i, str) for i in date_range):
                self._datelist, self._isrange = validate_date_list_datestr(date_range, start_time, end_time)
            elif all(isinstance(i, dt.datetime) for i in date_range):
                self._datelist, self._isrange = validate_date_list_datetime(date_range, start_time, end_time)
            elif all(isinstance(i, dt.date) for i in date_range):
                self._datelist, self._isrange = validate_date_list_date(date_range, start_time, end_time)
            else:
                # input type is invalid
                # TODO: Flesh out this TypeError once this class is done
                raise TypeError("date_range must be a list of one of the following: \n")

    @property
    def datetimes(self):
        return self._datelist
    
    @property
    def is_range(self):
        return self._isrange

