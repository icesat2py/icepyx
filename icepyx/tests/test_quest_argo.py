import icepyx as ipx
import json
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
    reg_a = Argo([-154, 54, -151, 56], ["2023-01-20", "2023-01-29"])
    reg_a.search_data()
    obs_df = reg_a.profiles

    exp = 0
    with open("./icepyx/tests/argovis_test_data2.json") as file:
        data = json.load(file)
        for profile in data:
            exp = exp + len(profile["measurements"])

    assert exp == len(obs_df)

    # goal: check number of rows in df matches rows in json
    # approach: create json files with profiles and store them in test suite
    # then use those for the comparison
    # update: for some reason the file downloaded from argovis and the one created here had different lengths
    # by downloading the json from the url of the search here, they matched
    # next steps: testing argo bgc?
