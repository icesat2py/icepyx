import icepyx as ipx
import pytest
import warnings
from icepyx.quest.dataset_scripts.argo import Argo


def test_available_profiles():
    reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])
    obs_msg = reg_a.search_data()
    obs_cols = reg_a.profiles.columns

    exp_msg = "Found profiles - converting to a dataframe"
    exp_cols = [
        "pres",
        "temp",
        "cycle_number",
        "profile_id",
        "lat",
        "lon",
        "date",
        "psal",
    ]

    assert obs_msg == exp_msg
    assert set(exp_cols) == set(obs_cols)

    # print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())


def test_no_available_profiles():
    reg_a = Argo([-55, 68, -48, 71], ["2019-02-20", "2019-02-28"])
    obs = reg_a.search_data()

    exp = (
        "Warning: Query returned no profiles\n" "Please try different search parameters"
    )

    assert obs == exp


def test_fmt_coordinates():
    reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])
    obs = reg_a._fmt_coordinates()

    exp = "[[[-143.0,30.0],[-143.0,37.0],[-154.0,37.0],[-154.0,30.0],[-143.0,30.0]]]"

    assert obs == exp


def test_parse_into_df():
    reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])
    reg_a.search_data()

    pass

    # goal: check number of rows in df matches rows in json
    # approach: create json files with profiles and store them in test suite
    # then use those for the comparison
