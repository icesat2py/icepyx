import datetime as dt

import pytest

import icepyx.core.temporal as tp

# DevNote: this test suite needs to be parameterized (and fixtured) to include ALL acceptable input types
# Currently it tests most cases for lists and dicts where the input type is str
# A couple of tests were added for datetime.datetime type inputs, but they are incomplete
# dt.date type inputs remain untested


# ####### INCOMPLETE DT.DATETIME tests ###########


def test_range_dt_dt_list():
    start_dt = dt.datetime(2019, 2, 20, 0, 10, 0)
    end_dt = dt.datetime(2019, 2, 28, 14, 45, 30)
    result = tp.Temporal([start_dt, end_dt])
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 10, 0),
        dt.datetime(2019, 2, 28, 14, 45, 30),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_dt_dt_dict():
    start_dt = dt.datetime(2019, 2, 20, 0, 10, 0)
    end_dt = dt.datetime(2019, 2, 28, 14, 45, 30)
    result = tp.Temporal({"start_date": start_dt, "end_date": end_dt})
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 10, 0),
        dt.datetime(2019, 2, 28, 14, 45, 30),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_dt_date_list():
    start_dt = dt.date(2019, 2, 20)
    end_dt = dt.date(2019, 2, 28)
    result = tp.Temporal([start_dt, end_dt])
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 0, 0),
        dt.datetime(2019, 2, 28, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_dt_date_dict():
    start_dt = dt.date(2019, 2, 20)
    end_dt = dt.date(2019, 2, 28)
    result = tp.Temporal({"start_date": start_dt, "end_date": end_dt})
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 0, 0),
        dt.datetime(2019, 2, 28, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_dt_notime_list():
    start_dt = dt.datetime(2019, 2, 20)
    end_dt = dt.datetime(2019, 2, 28)
    result = tp.Temporal([start_dt, end_dt])
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 0, 0),
        dt.datetime(2019, 2, 28, 0, 0, 0),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_dt_notime_dict():
    start_dt = dt.datetime(2019, 2, 20)
    end_dt = dt.datetime(2019, 2, 28)
    result = tp.Temporal({"start_date": start_dt, "end_date": end_dt})
    expected_range = [
        dt.datetime(2019, 2, 20, 0, 0, 0),
        dt.datetime(2019, 2, 28, 0, 0, 0),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


# ####### BEGIN DATE RANGE TESTS ###########


def test_range_str_yyyymmdd_list_no_start_end_time():
    result = tp.Temporal(["2016-01-01", "2020-01-01"])
    expected_range = [
        dt.datetime(2016, 1, 1, 0, 0, 0),
        dt.datetime(2020, 1, 1, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_list_no_start_end_time():
    result = tp.Temporal(["2016-14", "2020-40"])
    expected_range = [
        dt.datetime(2016, 1, 14, 0, 0, 0),
        dt.datetime(2020, 2, 9, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyymmdd_dict_no_start_end_time():
    result = tp.Temporal({"start_date": "2016-01-01", "end_date": "2020-01-01"})
    expected_range = [
        dt.datetime(2016, 1, 1, 0, 0, 0),
        dt.datetime(2020, 1, 1, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_dict_no_start_end_time():
    result = tp.Temporal({"start_date": "2016-14", "end_date": "2020-40"})
    expected_range = [
        dt.datetime(2016, 1, 14, 0, 0, 0),
        dt.datetime(2020, 2, 9, 23, 59, 59),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


# Test using actual start/end time inputs

# string start/end


def test_range_str_yyyymmdd_list_string_start_end():
    result = tp.Temporal(["2016-01-01", "2020-01-01"], "01:00:00", "13:10:01")
    expected_range = [
        dt.datetime(2016, 1, 1, 1, 0, 0),
        dt.datetime(2020, 1, 1, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_list_string_start_end():
    result = tp.Temporal(["2016-14", "2020-40"], "01:00:00", "13:10:01")
    expected_range = [
        dt.datetime(2016, 1, 14, 1, 0, 0),
        dt.datetime(2020, 2, 9, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyymmdd_dict_string_start_end():
    result = tp.Temporal(
        {"start_date": "2016-01-01", "end_date": "2020-01-01"}, "01:00:00", "13:10:01"
    )
    expected_range = [
        dt.datetime(2016, 1, 1, 1, 0, 0),
        dt.datetime(2020, 1, 1, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_dict_string_start_end():
    result = tp.Temporal(
        {"start_date": "2016-14", "end_date": "2020-40"}, "01:00:00", "13:10:01"
    )
    expected_range = [
        dt.datetime(2016, 1, 14, 1, 0, 0),
        dt.datetime(2020, 2, 9, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


# dt.time start/end


def test_range_str_yyyymmdd_list_time_start_end():
    result = tp.Temporal(
        ["2016-01-01", "2020-01-01"], dt.time(1, 0, 0), dt.time(13, 10, 1)
    )
    expected_range = [
        dt.datetime(2016, 1, 1, 1, 0, 0),
        dt.datetime(2020, 1, 1, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_list_time_start_end():
    result = tp.Temporal(["2016-14", "2020-40"], dt.time(1, 0, 0), dt.time(13, 10, 1))
    expected_range = [
        dt.datetime(2016, 1, 14, 1, 0, 0),
        dt.datetime(2020, 2, 9, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyymmdd_dict_time_start_end():
    result = tp.Temporal(
        {"start_date": "2016-01-01", "end_date": "2020-01-01"},
        dt.time(1, 0, 0),
        dt.time(13, 10, 1),
    )
    expected_range = [
        dt.datetime(2016, 1, 1, 1, 0, 0),
        dt.datetime(2020, 1, 1, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


def test_range_str_yyyydoy_dict_time_start_end():
    result = tp.Temporal(
        {"start_date": "2016-14", "end_date": "2020-40"},
        dt.time(1, 0, 0),
        dt.time(13, 10, 1),
    )
    expected_range = [
        dt.datetime(2016, 1, 14, 1, 0, 0),
        dt.datetime(2020, 2, 9, 13, 10, 1),
    ]
    assert result.start == expected_range[0]
    assert result.end == expected_range[1]


# Date Range Errors


# (The following inputs are bad, testing to ensure the temporal class handles this elegantly)
def test_bad_start_time_type():
    with pytest.raises(AssertionError):
        tp.Temporal(["2016-01-01", "2020-01-01"], 100000, "13:10:01")


def test_bad_end_time_type():
    with pytest.raises(AssertionError):
        tp.Temporal(["2016-01-01", "2020-01-01"], "01:00:00", 131001)


def test_range_bad_list_len():
    with pytest.raises(ValueError):
        tp.Temporal(["2016-01-01", "2020-01-01", "2022-02-15"])


def test_range_str_bad_yyyydoy():
    with pytest.raises(AssertionError):
        tp.Temporal(["2016-01-01", "2020-01-01"], "01:00:00", 131001)


def test_range_str_bad_yyyymmdd():
    with pytest.raises(AssertionError):
        tp.Temporal(["2016-01-01", "2020-01-01"], "01:00:00", 131001)


# a "bad dict" is assumed to be one of the wrong length or with the wrong key names
def test_bad_dict_keys():
    with pytest.raises(ValueError):
        tp.Temporal({"startdate": "2016-01-01", "enddate": "2020-01-01"})


def test_bad_dict_length():
    with pytest.raises(ValueError):
        tp.Temporal({"start_date": "2016-01-01"})


# A "bad range" is a range where the start_date > end date
def test_range_str_bad_range():
    with pytest.raises(AssertionError):
        tp.Temporal({"start_date": "2020-01-01", "end_date": "2016-01-01"})


# NOTE: Not testing bad datetime/time inputs because it is assumed the datetime library
# will throw errors if the user inputs a bad value of either type

# ####### END DATE RANGE TESTS #############
