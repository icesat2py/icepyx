import pytest

from icepyx.core.read import Read
import icepyx.core.read as read


def test_check_datasource_type():
    ermesg = "filepath must be a string or Path"
    with pytest.raises(TypeError, match=ermesg):
        read._check_datasource(246)


@pytest.mark.parametrize(
    "filepath, expect",
    [
        ("./", "is2_local"),
        (
            """s3://nsidc-cumulus-prod-protected/ATLAS/
            ATL03/006/2019/11/30/ATL03_20191130221008_09930503_006_01.h5""",
            "is2_s3",
        ),
    ],
)
def test_check_datasource(filepath, expect):
    source_type = read._check_datasource(filepath)
    assert source_type == expect


# not sure what I could enter here would get to the else...
# def test_unknown_datasource_type():
#     ermesg = "Could not confirm the datasource type."
#     with pytest.raises(ValueError, match=ermesg):
#         read._check_datasource("")


def test_validate_source_str_given_as_list():
    ermesg = "You must enter your input as a string."
    with pytest.raises(AssertionError, match=ermesg):
        read._validate_source(["/path/to/valid/ATL06_file.py"])


def test_validate_source_str_not_a_dir_or_file():
    ermesg = "Your data source string is not a valid data source."
    with pytest.raises(AssertionError, match=ermesg):
        read._validate_source("./fake/dirpath")
        read._validate_source("./fake_file.h5")


@pytest.mark.parametrize(
    "dir, fn_glob, expect",
    [
        (
            "./icepyx/**/",
            "is2*.py",
            sorted(
                [
                    "./icepyx/core/is2ref.py",
                    "./icepyx/tests/is2class_query.py",
                ]
            ),
        ),
        (
            "./icepyx/core/",
            "is2*.py",
            ["./icepyx/core/is2ref.py"],
        ),
        (
            "./icepyx/",
            "bogus_glob",
            [],
        ),
    ],
)
def test_parse_source(dir, fn_glob, expect):
    filelist = read._parse_source(dir + fn_glob, glob_kwargs={"recursive": True})
    print(filelist)
    print(expect)
    assert (sorted(filelist)) == expect


@pytest.mark.parametrize(
    "grp_path, exp_track_str, exp_spot_dim_name, exp_spot_var_name",
    [
        ("gt1l", "gt1l", "spot", "gt"),
        ("gt3r", "gt3r", "spot", "gt"),
        ("profile_2", "profile_2", "profile", "prof"),
        ("pt1", "pt1", "pair_track", "pt"),
    ],
)
def test_get_track_type_str(
    grp_path, exp_track_str, exp_spot_dim_name, exp_spot_var_name
):
    obs_track_str, obs_spot_dim_name, obs_spot_var_name = read._get_track_type_str(
        grp_path
    )
    assert (obs_track_str, obs_spot_dim_name, obs_spot_var_name) == (
        exp_track_str,
        exp_spot_dim_name,
        exp_spot_var_name,
    )


# Best way to test this may be by including a small sample file with the repo
# (which can be used for testing some of the catalog/read-in functions as well)
# def test_invalid_filename_pattern_in_file():
#     ermesg = "Your input filename does not match the specified pattern."
# default_pattern = Read("/path/to/valid/source/file")._filename_pattern
#     with pytest.raises(AssertionError, match=ermesg):
#         read._validate_source('/valid/filepath/with/non-default/filename/pattern.h5', default_pattern)

# def test_invalid_filename_pattern_in_dir():
#     ermesg = "None of your filenames match the specified pattern."
#     default_pattern = Read("/path/to/valid/dir/")._filename_pattern
#     with pytest.raises(AssertionError, match=ermesg):
#         read._validate_source('/valid/dirpath/with/non-default/filename/pattern.h5', default_pattern)
