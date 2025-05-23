import icepyx.core.variables as variables


def test_list_of_dict_vals():
    testdict = {
        "sc_orient": ["orbit_info/sc_orient"],
        "data_start_utc": ["ancillary_data/data_start_utc"],
        "data_end_utc": ["ancillary_data/data_end_utc"],
        "h_li": ["gt1l/land_ice_segments/h_li"],
        "latitude": ["gt1l/land_ice_segments/latitude"],
        "longitude": ["gt1l/land_ice_segments/longitude"],
    }

    obs = variables.list_of_dict_vals(testdict)
    exp = [
        "orbit_info/sc_orient",
        "ancillary_data/data_start_utc",
        "ancillary_data/data_end_utc",
        "gt1l/land_ice_segments/h_li",
        "gt1l/land_ice_segments/latitude",
        "gt1l/land_ice_segments/longitude",
    ]

    assert obs == exp
