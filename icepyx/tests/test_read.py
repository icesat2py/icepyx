import pytest

from icepyx.core.read import Read
import icepyx.core.read as read


# note isdir will issue a TypeError if a tuple is passed
def test_parse_source_bad_input_type():
    ermesg = (
        "data_source should be a list of files, a directory, the path to a file, "
        "or a glob string."
    )
    with pytest.raises(TypeError, match=ermesg):
        read._parse_source(150)
        read._parse_source({"myfiles": "./my_valid_path/file.h5"})


@pytest.mark.parametrize(
    "source, expect",
    [
        (  # check list input
            [
                "./icepyx/core/is2ref.py",
                "./icepyx/tests/is2class_query.py",
            ],
            sorted(
                [
                    "./icepyx/core/is2ref.py",
                    "./icepyx/tests/is2class_query.py",
                ]
            ),
        ),
        (  # check dir input
            "./examples",
            [
                "./examples/README.md",
            ],
        ),
        (  # check filename string with glob pattern input
            "./icepyx/**/is2*.py",
            sorted(
                [
                    "./icepyx/core/is2ref.py",
                    "./icepyx/tests/is2class_query.py",
                ]
            ),
        ),
        (  # check filename string without glob pattern input
            "./icepyx/core/is2ref.py",
            [
                "./icepyx/core/is2ref.py",
            ],
        ),
        (  # check s3 filename string
            (
                "s3://nsidc-cumulus-prod-protected/ATLAS/"
                "ATL03/006/2019/11/30/ATL03_20191130221008_09930503_006_01.h5"
            ),
            [
                (
                    "s3://nsidc-cumulus-prod-protected/ATLAS/"
                    "ATL03/006/2019/11/30/ATL03_20191130221008_09930503_006_01.h5"
                ),
            ],
        ),
        (
            "./icepyx/core/is2*.py",
            ["./icepyx/core/is2ref.py"],
        ),
        (  # check bad input
            "./icepyx/bogus_glob",
            [],
        ),
    ],
)
def test_parse_source(source, expect):
    filelist = read._parse_source(source, glob_kwargs={"recursive": True})
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
