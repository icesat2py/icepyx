import pytest

from icepyx.core.variables import Variables, list_of_dict_vals


@pytest.mark.parametrize(
    "input_dict, expected",
    [
        ({}, []),
        ({"a": [1, 2, 3], "b": [4, 5, 6]}, [1, 2, 3, 4, 5, 6]),
        ({"a": [1, 2, 3, 4, 5, 6], "b": []}, [1, 2, 3, 4, 5, 6]),
        ({"a": [1], "b": [2], "c": [3], "d": [4]}, [1, 2, 3, 4]),
        ({"a": [1], "b": [1], "c": [1], "d": [1]}, [1, 1, 1, 1]),
        (
            {
                "sc_orient": ["orbit_info/sc_orient"],
                "data_start_utc": ["ancillary_data/data_start_utc"],
                "data_end_utc": ["ancillary_data/data_end_utc"],
                "h_li": ["gt1l/land_ice_segments/h_li"],
                "latitude": ["gt1l/land_ice_segments/latitude"],
                "longitude": ["gt1l/land_ice_segments/longitude"],
            },
            [
                "orbit_info/sc_orient",
                "ancillary_data/data_start_utc",
                "ancillary_data/data_end_utc",
                "gt1l/land_ice_segments/h_li",
                "gt1l/land_ice_segments/latitude",
                "gt1l/land_ice_segments/longitude",
            ],
        ),
    ],
)
def test_list_of_dict_vals(input_dict, expected):
    assert list_of_dict_vals(input_dict) == expected


def test_list_of_dict_vals_old():
    testdict = {
        "sc_orient": ["orbit_info/sc_orient"],
        "data_start_utc": ["ancillary_data/data_start_utc"],
        "data_end_utc": ["ancillary_data/data_end_utc"],
        "h_li": ["gt1l/land_ice_segments/h_li"],
        "latitude": ["gt1l/land_ice_segments/latitude"],
        "longitude": ["gt1l/land_ice_segments/longitude"],
    }

    obs = list_of_dict_vals(testdict)
    exp = [
        "orbit_info/sc_orient",
        "ancillary_data/data_start_utc",
        "ancillary_data/data_end_utc",
        "gt1l/land_ice_segments/h_li",
        "gt1l/land_ice_segments/latitude",
        "gt1l/land_ice_segments/longitude",
    ]

    assert obs == exp


def test_variables():
    variables = Variables()
    assert variables is not None
    assert variables.variables == {}


def test_variable_path_and_product():
    with pytest.raises(TypeError):
        Variables(path="path", product="product")


def test_add_variable():
    variables = Variables()
    variables.add_variable("variable", "path")
    assert variables.variables == {"variable": "path"}
