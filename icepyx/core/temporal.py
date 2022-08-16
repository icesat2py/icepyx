import datetime as dt
import warnings


'''
Helper functions for validation of dates
'''


def convert_string_to_date(date):
    """
    Converts a string to a datetime object.
    Throws an error if an invalid format is passed in.

    Parameters
    ----------
    date: a string containing the date value.
    Current supported date formats are:

    "YYYY-MM-DD"
    "YYYY-DOY"


    Returns
    -------
    datetime object, representing the date from the string parameter.
    """
    for fmt in ('%Y-%m-%d', '%Y-%-j', '%Y-%j'):
        try:
            return dt.datetime.strptime(date, fmt)
        except ValueError:
            pass
    # TODO: "complete" this error so it's more informative
    raise ValueError('No valid date format found. The following formats are accepted:\n'
                     '%Y-%m-%d\n'
                     '%Y-%-j\n'
                     '%Y-%j\n')


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

    assert start.date() <= end.date(), "Your date range is invalid; end date MUST be on or after the start date."


def validate_times(start_time, end_time):

    """
    Validates the start and end times passed into __init__ function and returns them as datetime.time objects OR
    None type objects.



    Parameters
    ----------
    start_time: Start time, can be one of: str, datetime.time
    end_time:  End time, can be one of: str, datetime.time

    Returns
    -------
    start_time, end_time as datetime.time objects OR None type objects (i.e. if one of the parameters is a None type)
    """
    valid_time_types = (str, dt.time)

    # Validate start/end time types; then convert them to the appropriate datetime object
    if start_time is not None:
        # user specified a start time, need to first check if it's a valid type (if not, throw an AssertionError)
        assert isinstance(start_time, valid_time_types), "start_time must be one of the following types: \n" \
                                                         "str (format: HH:MM:SS)\n" \
                                                         "datetime.time"

        # if start_time is a string, then it must be converted to a datetime using strptime
        if isinstance(start_time, str):
            start_time = dt.datetime.strptime(start_time, "%H:%M:%S").time()

    if end_time is not None:
        # user specified an end time, need to first check if it's a valid type (if not, throw an AssertionError)
        assert isinstance(end_time, valid_time_types), "end_time must be one of the following types: \n" \
                                                       "str (format: HH:MM:SS)\n" \
                                                       "datetime.time"
        # if end_time is a string, then it must be converted to a datetime using strptime
        if not isinstance(end_time, dt.time):
            end_time = dt.datetime.strptime(end_time, "%H:%M:%S").time()

    return start_time, end_time

def validate_date_range_datestr(date_range, start_time, end_time):

    """
    Validates a date RANGE provided in the form of a list of strings (list must be of length 2).
    Strings must be of formats accepted by validate_inputs_temporal.convert_string_to_date().


    Returns the start and end datetimes as datetime objects
    by combining the start/end dates with their respective start/end times.

    If start and/or end times are not provided, the default options are 00:00:00 and 23:59:59, respectively.
    """
    # Check if start format is valid
    _start = convert_string_to_date(date_range[0])

    # Check if end format is valid
    _end = convert_string_to_date(date_range[1])

    # Check if date range passed in is valid
    check_valid_date_range(_start, _end)

    if start_time is None:
        # if user did not specify a start time, default to start time of 00:00:00
        start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()

    if end_time is None:
        end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()

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

    Returns the start and end datetimes as datetime objects.


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

    If start and/or end times are not provided, the default options are 00:00:00 and 23:59:59, respectively.



    """

    check_valid_date_range(date_range[0], date_range[1])

    if start_time is None:
        # if user did not specify a start time, default to start time of 00:00:00
        start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()

    if end_time is None:
        end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()

    _start = dt.datetime.combine(
        date_range[0], start_time
    )

    _end = dt.datetime.combine(
        date_range[1], end_time
    )

    return _start, _end


def validate_date_range_dict(date_range, start_time, end_time):

    """
     Validates a date RANGE provided in the form of a dict with the following keys:
         start_date: start date, type can be of dt.datetime, dt.date, or string
         end_date: end date, type can be of dt.datetime, dt.date, or string

      Keys MUST have the exact names/formatting above or a ValueError will be thrown by this function.
      If the keys are of type dt.datetime, the start_time/end_time parameters will be ignored!

     Returns the start and end datetimes as datetime objects
     by combining the start/end dates with their respective start/end times (if the dict type is not datetime).

     If start and/or end times are not provided, the default options are 00:00:00 and 23:59:59, respectively.
     """

    # Try to get keys from date_range dict
    _start_date = date_range.get("start_date")
    _end_date = date_range.get("end_date")

    # If either is none, then we can assume bad keys and raise a ValueError for the user

    if _start_date is None or _end_date is None:
        raise ValueError("Dicts containing date ranges must have the following keys:\n"
                         "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
                         "end_date: end date, type can be of dt.datetime, dt.date, or string")

    # Ensure the date range is valid

    check_valid_date_range(convert_string_to_date(_start_date), convert_string_to_date(_end_date))

    # start_date

    #  if is datetime
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

        _start_date = dt.datetime.combine(
            _start_date, start_time
        )

    # if is string date
    elif isinstance(_start_date, str):
        if start_time is None:
            # if user did not specify a start time, default to start time of 00:00:00
            start_time = dt.datetime.strptime("00:00:00", "%H:%M:%S").time()

        _start_date = convert_string_to_date(_start_date)

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

        _end_date = dt.datetime.combine(
            _end_date, end_time
        )

        # if is string date
    elif isinstance(_end_date, str):
        if end_time is None:
            end_time = dt.datetime.strptime("23:59:59", "%H:%M:%S").time()

        _end_date = convert_string_to_date(_end_date)

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

        start_time, end_time = validate_times(start_time, end_time)

        if len(date_range) == 2:

            # can be date objects, dicts, datetime objects, DOY input (YYYY-DOY)

            # date range is provided as dict of strings, dates, or datetimes
            if isinstance(date_range, dict):
                self._start, self._end = validate_date_range_dict(date_range, start_time, end_time)
            # date range is provided as list of strings
            elif all(isinstance(i, str) for i in date_range):
                self._start, self._end = validate_date_range_datestr(date_range, start_time, end_time)
            # date range is provided as list of datetimes
            elif all(isinstance(i, dt.datetime) for i in date_range):
                self._start, self._end = validate_date_range_datetime(date_range, start_time, end_time)
            # date range is provided as list of dates
            elif all(isinstance(i, dt.date) for i in date_range):
                self._start,  self._end = validate_date_range_date(date_range, start_time, end_time)
            else:
                # input type is invalid
                raise TypeError("date_range must be a list of one of the following: \n"
                                "   list of strs with one of the following formats: \n"
                                "       YYYY-MM-DD, YYYY-DOY \n"
                                "   list of datetime.date or datetime.datetime objects \n"
                                "   dict with the following keys:\n"
                                "       start_date: start date, type can be datetime.datetime, datetime.date, or str\n"
                                "       end_date: end date, type can be datetime.datetime, datetime.date, or str\n"
                                )

        else:
            raise ValueError(
                "Your date range list is the wrong length. It should be of length 2, with start and end dates only."
            )

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
