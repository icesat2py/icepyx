import datetime as dt
from dateutil import parser
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


def validate_date_range_datestr(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of strings (list must be of length 2).
    Strings must be of format: "YYYY-MM-DD" (Otherwise, datetime.strptime() will throw ValueError)

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """
    # Check if start format is valid
    _start = parser.parse(date_range[0])

    # Check if end format is valid
    _end = parser.parse(date_range[1])

    check_valid_date_range(_start, _end)

    if start_time is None:
        # if user did not specify a start time, default to start time of 00:00:00
        start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()
    else:
        if isinstance(start_time, dt.datetime):
            start_time = start_time.time()

    if end_time is None:
        end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()
    else:
        if isinstance(end_time, dt.datetime):
            end_time = end_time.time()

    _start = dt.datetime.combine(
            _start, start_time
        )

    _end = dt.datetime.combine(
            _end, end_time
        )

    return _start, _end


def validate_date_range_datetime(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of datetime objects (list must be of length 2).

    TODO: if start_time OR end_time are not none, throw a warning! These will be ignored
    in favor of the times inside of the date_range datetime objects.

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """

    check_valid_date_range(date_range[0], date_range[1])

    if end_time is not None:
        warnings.warn("Warning: \"start_date\" given as datetime, but start_time argument was provided. \n"
                      "This argument will be ignored and the time from the start_date datetime object"
                      " will be used as start times.")
    if start_time is not None:
        warnings.warn("Warning: \"end_date\" given as datetime, but end_time argument was provided. \n"
                      "This argument will be ignored and the time from the end_date datetime object"
                      " will be used as end times.")

    return date_range[0], date_range[1]


def validate_date_range_date(date_range, start_time, end_time):

    """

    Validates a date RANGE provided in the form of a list of Date objects (list must be of length 2).

    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    """

    check_valid_date_range(date_range[0], date_range[1])

    if start_time is not None:
        start_time = dt.datetime.strptime(start_time, "%H:%M:%S")
    else:
        # if user did not specify a start time, default to start time of 00:00:00
        start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S")

    if end_time is not None:
        end_time = dt.datetime.strptime(end_time, "%H:%M:%S")
    else:
        end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S")

    _start = dt.datetime.combine(
        date_range[0], start_time.time()
    )

    _end = dt.datetime.combine(
        date_range[1], end_time.time()
    )

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
        if start_time is None:
            start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()
        else:
            if isinstance(start_time, dt.datetime):
                start_time = start_time.time()

        _start_date = dt.datetime.combine(
            _start_date, start_time
        )

    # if is string date
    elif isinstance(_start_date, str):
        if start_time is None:
            # if user did not specify a start time, default to start time of 00:00:00
            start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()
        else:
            if isinstance(start_time, dt.datetime):
                start_time = start_time.time()

        _start_date = parser.parse(_start_date)

        _start_date = dt.datetime.combine(
            _start_date, start_time
        )
    #   else; raise valueerror, some invalid type
    else:
        raise ValueError("Invalid type for key 'start_date'.\n"
                         "Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

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
        if end_time is None:
            end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()
        else:
            if isinstance(end_time, dt.datetime):
                end_time = end_time.time()

        _end_date = dt.datetime.combine(
            _end_date, end_time
        )

        # if is string date
    elif isinstance(_end_date, str):
        if end_time is None:
            end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()
        _end_date = parser.parse(_end_date)

        _end_date = dt.datetime.combine(
            _end_date, end_time
        )

        #   else; raise valueerror, some invalid type
    else:
        raise ValueError("Invalid type for key 'end_date'.\n"
                         "Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

    return _start_date, _end_date



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
        # else:
            # if user did not specify a start time, default to start time of 00:00:00
            # start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S")

        if end_time is not None:
            # user specified an end time, need to first check if it's a valid type (if not, throw an AssertionError)
            assert isinstance(end_time, valid_time_types), "end_time must be one of the following types: \n" \
                                                             "str (format: HH:MM:SS)\n" \
                                                             "datetime.time"
            # if end_time is a string, then it must be converted to a datetime using strptime
            if not isinstance(end_time, dt.time):
                end_time = dt.datetime.strptime(end_time, "%H:%M:%S")

        # else:
            # if user did not specify an end time, default to end time of 23:59:59
            # end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S")

        if len(date_range) == 2:
            # range, list of dates
            # can be date objects, dicts, datetime objects, DOY input (YYYY-DOY)
            if isinstance(date_range, dict):
                self._start, self._end = validate_date_range_dict(date_range, start_time, end_time)
            elif all(isinstance(i, str) for i in date_range):
                self._start, self._end = validate_date_range_datestr(date_range, start_time, end_time)
            elif all(isinstance(i, dt.datetime) for i in date_range):
                self._start, self._end = validate_date_range_datetime(date_range, start_time, end_time)
            elif all(isinstance(i, dt.date) for i in date_range):
                self._start,  self._end = validate_date_range_date(date_range, start_time, end_time)
            else:
                # input type is invalid
                # TODO: Flesh out this TypeError once this class is done
                raise TypeError("date_range must be a list of one of the following: \n")

        else:
            raise ValueError(
                "Your date range list is the wrong length. It should have start and end dates only."
            )

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end



