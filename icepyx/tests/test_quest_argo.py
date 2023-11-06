import pytest
import re

from icepyx.quest.quest import Quest

# create an Argo instance via quest (Argo is a submodule)
def argo_quest_instance(bounding_box, date_range):
    my_quest = Quest(spatial_extent=bounding_box, date_range=date_range)
    my_quest.add_argo()
    my_argo = my_quest.datasets["argo"]

    return my_argo


def test_available_profiles():
    reg_a = argo_quest_instance([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])
    obs_msg = reg_a.search_data()

    exp_msg = "19 valid profiles have been identified"

    assert obs_msg == exp_msg


def test_no_available_profiles():
    reg_a = argo_quest_instance([-55, 68, -48, 71], ["2019-02-20", "2019-02-28"])
    obs = reg_a.search_data()

    exp = (
        "Warning: Query returned no profiles\n" "Please try different search parameters"
    )

    assert obs == exp


def test_fmt_coordinates():
    reg_a = argo_quest_instance([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])
    obs = reg_a._fmt_coordinates()

    exp = "[[-143.0,30.0],[-143.0,37.0],[-154.0,37.0],[-154.0,30.0],[-143.0,30.0]]"

    assert obs == exp


def test_invalid_param():
    reg_a = argo_quest_instance([-154, 30, -143, 37], ["2022-04-12", "2022-04-26"])

    invalid_params = ["temp", "temperature_files"]

    ermsg = re.escape(
        "Parameter '{0}' is not valid. Valid parameters are {1}".format(
            "temp", reg_a._valid_params()
        )
    )

    with pytest.raises(AssertionError, match=ermsg):
        reg_a._validate_parameters(invalid_params)


def test_download_parse_into_df():
    reg_a = argo_quest_instance([-154, 30, -143, 37], ["2022-04-12", "2022-04-13"])
    reg_a.download(params=["salinity"])  # note: pressure is returned by default

    obs_cols = reg_a.argodata.columns

    exp_cols = [
        "salinity",
        "salinity_argoqc",
        "pressure",
        "profile_id",
        "lat",
        "lon",
        "date",
    ]

    assert set(exp_cols) == set(obs_cols)

    assert len(reg_a.argodata) == 1942


# approach for additional testing of df functions: create json files with profiles and store them in test suite
# then use those for the comparison (e.g. number of rows in df and json match)


def test_merge_df():
    reg_a = argo_quest_instance([-150, 30, -120, 60], ["2022-06-07", "2022-06-14"])
    param_list = ["salinity", "temperature", "down_irradiance412"]

    df = reg_a.download(params=param_list)

    assert "down_irradiance412" in df.columns
    assert "down_irradiance412_argoqc" in df.columns

    df = reg_a.download(["doxy"], keep_existing=True)
    assert "doxy" in df.columns
    assert "doxy_argoqc" in df.columns
    assert "down_irradiance412" in df.columns
    assert "down_irradiance412_argoqc" in df.columns


def test_presRange_input_param():
    reg_a = argo_quest_instance([-154, 30, -143, 37], ["2022-04-12", "2022-04-13"])
    df = reg_a.download(params=["salinity"], presRange="0.2,180")

    assert df["pressure"].min() >= 0.2
    assert df["pressure"].max() <= 180
    assert "salinity" in df.columns
