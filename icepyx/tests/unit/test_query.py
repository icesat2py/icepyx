import icepyx as ipx

# ------------------------------------
# 		Generic Query tests
# ------------------------------------

# seem to be adequately covered in docstrings;
# may want to focus on testing specific queries


# ------------------------------------
# 		icepyx-specific tests
# ------------------------------------
def test_icepyx_boundingbox_query():
    reg_a = ipx.Query(
        "ATL06",
        [-64, 66, -55, 72],
        ["2019-02-22", "2019-02-28"],
        start_time="03:30:00",
        end_time="21:30:00",
        version="6",
    )
    obs_tuple = (
        reg_a.product,
        reg_a.dates,
        reg_a.start_time,
        reg_a.end_time,
        reg_a.product_version,
        reg_a.spatial_extent,
    )
    exp_tuple = (
        "ATL06",
        ["2019-02-22", "2019-02-28"],
        "03:30:00",
        "21:30:00",
        "006",
        ("bounding_box", [-64.0, 66.0, -55.0, 72.0]),
    )

    assert obs_tuple == exp_tuple


def test_temporal_properties_cycles_tracks():
    reg_a = ipx.Query(
        "ATL06",
        [-55, 68, -48, 71],
        cycles=["03", "04", "05", "06", "07"],
        tracks=["0849", "0902"],
    )
    exp = ["No temporal parameters set"]
    assert [obs == exp for obs in (reg_a.dates, reg_a.start_time, reg_a.end_time)]


def test_cmrparams_concept_id_matches_version():
    """
    Test that CMRparams uses the correct concept_id for the specified version.
    This test ensures that when building CMR search parameters, the concept_id
    retrieved matches the query's product version. A mismatch would result in
    querying granules from the wrong version.

    Regression test for: https://github.com/icesat2py/icepyx/issues/XXX
    When version=None was passed to _get_concept_id, earthaccess would return
    the first available collection, causing version 006 to be used instead of
    the intended version 007 or user-specified version.
    """
    # Concept IDs for ATL06 versions
    v006_concept_id = "C2670138092-NSIDC_CPRD"
    v007_concept_id = "C3564876127-NSIDC_CPRD"

    # Test 1: Explicit version 006
    reg_v006 = ipx.Query(
        "ATL06",
        [-45, 58, -35, 75],
        ["2019-11-30", "2019-11-30"],
        version="006",
    )
    assert reg_v006.product_version == "006"
    assert reg_v006.CMRparams["concept_id"] == v006_concept_id

    # Test 2: Explicit version 007
    reg_v007 = ipx.Query(
        "ATL06",
        [-45, 58, -35, 75],
        ["2019-11-30", "2019-11-30"],
        version="007",
    )
    assert reg_v007.product_version == "007"
    assert reg_v007.CMRparams["concept_id"] == v007_concept_id

    # Test 3: Default version (should use latest, which is 007)
    reg_default = ipx.Query(
        "ATL06",
        [-45, 58, -35, 75],
        ["2019-11-30", "2019-11-30"],
    )
    assert reg_default.product_version == "007"
    assert reg_default.CMRparams["concept_id"] == v007_concept_id
