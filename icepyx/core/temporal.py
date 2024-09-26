import datetime as dt
import warnings

"""
Helper functions for validation of dates
"""


def convert_string_to_date(date):
    """
    Converts a string to a datetime object.
    Throws an error if an invalid format is passed in.

    Parameters
    ----------
    date: string
        A string representation for the date value. Current supported date formats are:
            * "YYYY-MM-DD"
            * "YYYY-DOY"

    Returns
    -------
    datetime.date object, representing the date from the string parameter.

    Examples
    --------
    >>> mmdd = "2016-01-01"
    >>> converted = convert_string_to_date(mmdd)
    >>> converted
    datetime.date(2016, 1, 1)

    >>> doy = "2020-40"
    >>> converted = convert_string_to_date(doy)
    >>> converted
    datetime.date(2020, 2, 9)

    """

    for fmt in ("%Y-%m-%d", "%Y-%-j", "%Y-%j"):
        try:
            return dt.datetime.strptime(date, fmt).date()
        except ValueError:
            pass
    raise ValueError(
        "No valid date format found. The following formats are accepted:\n"
        "%Y-%m-%d\n"
        "%Y-%-j\n"  # skips leading zeros
        "%Y-%j\n"
    )


def check_valid_date_range(start, end):
    """
    Helper function for checking if a date range is valid.

    AssertionError is raised if the start date is later than the end date.

    Parameters
    ----------
    start: datetime.datetime, datetime.date
        Starting date of date range to check.
    end: datetime.datetime, datetime.date
        Ending date of date range to check

    Returns
    -------
    boolean (true if date range is valid, false otherwise)

    Examples
    --------
    >>> start = dt.datetime.strptime("2016-01-01", "%Y-%m-%d")
    >>> end = dt.datetime.strptime("2020-01-01", "%Y-%m-%d")
    >>> drange = check_valid_date_range(start, end)
    >>> drange


    >>> drange = check_valid_date_range(end, start) # doctest: +SKIP
    AssertionError: Your date range is invalid; end date MUST be on or after the start date.
    """
    if isinstance(start, dt.datetime):
        start = start.date()
    if isinstance(end, dt.datetime):
        end = end.date()
    assert (
        start <= end
    ), "Your date range is invalid; end date MUST be on or after the start date."


def validate_times(start_time, end_time):
    """
    Validates the start and end times passed into __init__ and returns them as datetime.time objects.

    NOTE: If start and/or end times are not provided (are of type None), the defaults are 00:00:00 and 23:59:59, respectively.

    Parameters
    ----------
    start_time: string, datetime.time, None
    end_time:  string, datetime.time, None

    Returns
    -------
    start_time, end_time as datetime.time objects

    Examples
    --------
    >>> val_time = validate_times("00:00:00", "23:59:59")
    >>> val_time
    (datetime.time(0, 0), datetime.time(23, 59, 59))

    """
    valid_time_types = (str, dt.time)

    # Validate start/end time types; then convert them to the appropriate datetime object
    if start_time is not None:
        # user specified a start time, need to first check if it's a valid type (if not, throw an AssertionError)
        assert isinstance(start_time, valid_time_types), (
            "start_time must be one of the following types: \n"
            "str (format: HH:MM:SS)\n"
            "datetime.time"
        )

        # if start_time is a string, then it must be converted to a datetime using strptime
        if isinstance(start_time, str):
            start_time = dt.datetime.strptime(start_time, "%H:%M:%S").time()
    else:
        start_time = dt.time(0, 0, 0)

    if end_time is not None:
        # user specified an end time, need to first check if it's a valid type (if not, throw an AssertionError)
        assert isinstance(end_time, valid_time_types), (
            "end_time must be one of the following types: \n"
            "str (format: HH:MM:SS)\n"
            "datetime.time"
        )
        # if end_time is a string, then it must be converted to a datetime using strptime
        if not isinstance(end_time, dt.time):
            end_time = dt.datetime.strptime(end_time, "%H:%M:%S").time()
    else:
        end_time = dt.time(23, 59, 59)

    return start_time, end_time


def validate_date_range_datestr(date_range, start_time=None, end_time=None):
    """
    Validates a date range provided in the form of a list of strings.

    Combines the start and end dates with their respective start and end times
    to create complete start and end datetime.datetime objects.

    Parameters
    ----------
    date_range: list(str)
        A date range provided in the form of a list of strings
            Strings must be of formats accepted by validate_inputs_temporal.convert_string_to_date().
            List must be of length 2.
    start_time: string, datetime.time, None
    end_time:  string, datetime.time, None

    Returns
    -------
    Start and end dates and times as datetime.datetime objects

    Examples
    --------
    >>> daterange = validate_date_range_datestr(["2016-01-01", "2020-01-01"])
    >>> daterange
    (datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 59))

    """
    # Check if start format is valid
    _start = convert_string_to_date(date_range[0])

    # Check if end format is valid
    _end = convert_string_to_date(date_range[1])

    # Check if date range passed in is valid
    check_valid_date_range(_start, _end)

    start_time, end_time = validate_times(start_time, end_time)

    _start = dt.datetime.combine(_start, start_time)
    _end = dt.datetime.combine(_end, end_time)

    return _start, _end


def validate_date_range_datetime(date_range, start_time=None, end_time=None):
    """
    Validates a date range provided in the form of a list of datetimes.

    Parameters
    ----------
    date_range: list(datetime.datetime)
        A date range provided in the form of a list of datetimes.
        List must be of length 2.
    start_time: None, string, datetime.time
    end_time:  None, string, datetime.time

    NOTE: If start and/or end times are given,
    they will be **ignored** in favor of the time from the start/end datetime.datetime objects.

    Returns
    -------
    Start and end dates and times as datetime.datetime objects

    Examples
    --------
    >>> drange = [dt.datetime(2016, 1, 14, 1, 0, 0), dt.datetime(2020, 2, 9, 13, 10, 1)]
    >>> valid_drange = validate_date_range_datetime(drange)
    >>> valid_drange
    (datetime.datetime(2016, 1, 14, 1, 0), datetime.datetime(2020, 2, 9, 13, 10, 1))

    """

    check_valid_date_range(date_range[0], date_range[1])

    warnings.warn(
        "If you submitted datetime.datetime objects that were created without times, \n"
        "your time values will use the datetime package defaults of all 0s rather than \n"
        "the icepyx defaults or times entered using the `start_time` or `end_time` arguments."
    )

    return date_range[0], date_range[1]


def validate_date_range_date(date_range, start_time=None, end_time=None):
    """
    Validates a date range provided in the form of a list of datetime.date objects.

    Combines the start and end dates with their respective start and end times
    to create complete start and end datetime.datetime objects.

    Parameters
    ----------
    date_range: list(str)
        A date range provided in the form of a list of datetime.dates.
        List must be of length 2.
    start_time: string or datetime.time
    end_time:  string or datetime.time

    Returns
    -------
    Start and end datetimes as datetime.datetime objects

    Examples
    --------
    >>> drange = [dt.date(2016, 1, 1), dt.date(2020, 1, 1)]
    >>> valid_drange = validate_date_range_date(drange, "00:10:00", "21:00:59")
    >>> valid_drange
    (datetime.datetime(2016, 1, 1, 0, 10), datetime.datetime(2020, 1, 1, 21, 0, 59))

    """

    check_valid_date_range(date_range[0], date_range[1])
    start_time, end_time = validate_times(start_time, end_time)

    _start = dt.datetime.combine(date_range[0], start_time)
    _end = dt.datetime.combine(date_range[1], end_time)

    return _start, _end


def validate_date_range_dict(date_range, start_time=None, end_time=None):
    """
    Validates a date range provided in the form of a dict with the following keys:


    Parameters
    ----------
    date_range: dict(str, datetime.datetime, datetime.date)
        A date range provided in the form of a dict.
        date_range must contain only the following keys:
            *  `start_date`: start date, type can be of dt.datetime, dt.date, or string
            *  `end_date`: end date, type can be of dt.datetime, dt.date, or string
        Keys MUST have the exact names/formatting above or a ValueError will be thrown by this function.

        If the values are of type dt.datetime and were created without times,
        the datetime package defaults of all 0s are used and
        the start_time/end_time parameters will be ignored!
    start_time: string or datetime.time
    end_time:  string or datetime.time


    Returns
    -------
    Start and end datetimes as datetime.datetime objects
    (by combining the start/end dates with their respective start/end times, if the dict type is not datetime)

    Examples
    --------
    >>> drange = {"start_date": "2016-01-01", "end_date": "2020-01-01"}
    >>> valid_drange = validate_date_range_dict(drange, "00:00:00", "23:59:59")
    >>> valid_drange
    (datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 59))

    """

    # Try to get keys from date_range dict
    _start_date = date_range.get("start_date")
    _end_date = date_range.get("end_date")

    # If either is none, then we can assume bad keys and raise a ValueError for the user

    if _start_date is None or _end_date is None:
        raise ValueError(
            "Dicts containing date ranges must have the following keys:\n"
            "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
            "end_date: end date, type can be of dt.datetime, dt.date, or string"
        )

    start_time, end_time = validate_times(start_time, end_time)

    # start_date

    #  if is datetime
    if isinstance(_start_date, dt.datetime):
        pass

    # if is only date
    elif isinstance(_start_date, dt.date):
        _start_date = dt.datetime.combine(_start_date, start_time)

    # if is string date
    elif isinstance(_start_date, str):
        _start_date = convert_string_to_date(_start_date)
        _start_date = dt.datetime.combine(_start_date, start_time)

    #   else; raise valueerror, some invalid type
    else:
        raise ValueError(
            "Invalid type for key 'start_date'.\n"
            "Dicts containing date ranges must have the following keys:\n"
            "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
            "end_date: end date, type can be of dt.datetime, dt.date, or string"
        )

    # ######################### end_date #######################################
    # if is datetime

    if isinstance(_end_date, dt.datetime):
        pass

    # if is only date
    elif isinstance(_end_date, dt.date):
        _end_date = dt.datetime.combine(_end_date, end_time)

    # if is string date
    elif isinstance(_end_date, str):
        _end_date = convert_string_to_date(_end_date)
        _end_date = dt.datetime.combine(_end_date, end_time)

    # else; raise valueerror, some invalid type
    else:
        raise ValueError(
            "Invalid type for key 'end_date'.\n"
            "Dicts containing date ranges must have the following keys:\n"
            "start_date: start date, type can be of dt.datetime, dt.date, or string\n"
            "end_date: end date, type can be of dt.datetime, dt.date, or string"
        )

    # Ensure the date range is valid
    check_valid_date_range(_start_date, _end_date)

    return _start_date, _end_date


class Temporal:
    def __init__(self, date_range, start_time=None, end_time=None):
        """
        Validates input from "date_range" argument (and start/end time arguments, if provided),
        then creates a Temporal object with validated inputs as properties of the object.

        Temporal objects are to be used by icepyx.Query to store validated temporal information
        required by the Query.

        Parameters
        ----------
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
            If a datetime.datetime object was created without times, the datetime package defaults will apply over those of icepyx
        """

        if len(date_range) == 2:
            # date range is provided as dict of strings, dates, or datetimes
            if isinstance(date_range, dict):
                self._start, self._end = validate_date_range_dict(
                    date_range, start_time, end_time
                )

            # date range is provided as list of strings
            elif all(isinstance(i, str) for i in date_range):
                self._start, self._end = validate_date_range_datestr(
                    date_range, start_time, end_time
                )

            # date range is provided as list of datetimes
            elif all(isinstance(i, dt.datetime) for i in date_range):
                self._start, self._end = validate_date_range_datetime(
                    date_range, start_time, end_time
                )

            # date range is provided as list of dates
            elif all(isinstance(i, dt.date) for i in date_range):
                self._start, self._end = validate_date_range_date(
                    date_range, start_time, end_time
                )

            else:
                # input type is invalid
                raise TypeError(
                    "date_range must be a list of one of the following: \n"
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

    def __str__(self):
        return "Start date and time: {0}\nEnd date and time: {1}".format(
            self._start.strftime("%Y-%m-%d %H:%M:%S"),
            self._end.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @property
    def start(self):
        """
        Return the start date and time of the Temporal object as a datetime.datetime object.

        Examples
        -------
        >>> tmp_a = Temporal(["2016-01-01", "2020-01-01"])
        >>> tmp_a.start
        datetime.datetime(2016, 1, 1, 0, 0)

        """
        return self._start

    @property
    def end(self):
        """
        Return the end date and time of the Temporal object as a datetime.datetime object.

        Examples
        -------
        >>> tmp_a = Temporal(["2016-01-01", "2020-01-01"])
        >>> tmp_a.end
        datetime.datetime(2020, 1, 1, 23, 59, 59)

        """
        return self._end
