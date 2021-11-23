import json
import numpy as np
import requests
import warnings
from xml.etree import ElementTree as ET


import icepyx

# ICESat-2 specific reference functions
# options to get customization options for ICESat-2 data (though could be used generally)


def _validate_product(product):
    """
    Confirm a valid ICESat-2 product was specified
    """
    if isinstance(product, str):
        product = str.upper(product)
        assert product in [
            "ATL01",
            "ATL02",
            "ATL03",
            "ATL04",
            "ATL06",
            "ATL07",
            "ATL08",
            "ATL09",
            "ATL10",
            "ATL11",
            "ATL12",
            "ATL13",
        ], "Please enter a valid product"
    else:
        raise TypeError("Please enter a product string")
    return product


# DevGoal: See if there's a way to dynamically get this list so it's automatically updated


def _validate_OA_product(product):
    """
    Confirm a valid ICESat-2 product was specified
    """
    if isinstance(product, str):
        product = str.upper(product)
        assert product in [
            "ATL06",
            "ATL07",
            "ATL08",
            "ATL10",
            "ATL12",
            "ATL13",
        ], "Oops! Elevation visualization only supports products ATL06, ATL07, ATL08, ATL10, ATL12, ATL13; please try another product."
    else:
        raise TypeError("Please enter a product string")
    return product


# DevNote: test for this function is commented out; dates in some of the values were causing the test to fail...
def about_product(prod):
    """
    Ping Earthdata to get metadata about the product of interest (the collection).

    See Also
    --------
    query.Query.product_all_info
    """

    cmr_collections_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    response = requests.get(cmr_collections_url, params={"short_name": prod})
    results = json.loads(response.content)
    return results


# DevGoal: use a mock of this output to test later functions, such as displaying options and widgets, etc.
def _get_custom_options(session, product, version):
    """
    Get lists of what customization options are available for the product from NSIDC.
    """
    cust_options = {}

    if session is None:
        raise ValueError(
            "Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)"
        )

    capability_url = (
        f"https://n5eil02u.ecs.nsidc.org/egi/capabilities/{product}.{version}.xml"
    )
    response = session.get(capability_url)
    root = ET.fromstring(response.content)

    # collect lists with each service option
    subagent = [subset_agent.attrib for subset_agent in root.iter("SubsetAgent")]
    cust_options.update({"options": subagent})

    # reformatting
    formats = [Format.attrib for Format in root.iter("Format")]
    format_vals = [formats[i]["value"] for i in range(len(formats))]
    format_vals.remove("")
    cust_options.update({"fileformats": format_vals})

    # reprojection only applicable on ICESat-2 L3B products.

    # reprojection options
    projections = [Projection.attrib for Projection in root.iter("Projection")]
    proj_vals = []
    for i in range(len(projections)):
        if (projections[i]["value"]) != "NO_CHANGE":
            proj_vals.append(projections[i]["value"])
    cust_options.update({"reprojectionONLY": proj_vals})

    # reformatting options that do not support reprojection
    exclformats_all = []
    for i in range(len(projections)):
        if "excludeFormat" in projections[i]:
            exclformats_str = projections[i]["excludeFormat"]
            exclformats_all.append(exclformats_str.split(","))
    exclformats_list = [
        item for sublist in exclformats_all for item in sublist
    ]  # list only unique formats
    no_proj = list(set(exclformats_list))
    cust_options.update({"noproj": no_proj})

    # reformatting options that support reprojection
    format_proj = []
    for i in range(len(format_vals)):
        if format_vals[i] not in no_proj:
            format_proj.append(format_vals[i])
    cust_options.update({"formatreproj": format_proj})

    # variable subsetting
    vars_raw = []

    def get_varlist(elem):
        childlist = list(elem)
        if len(childlist) == 0 and elem.tag == "SubsetVariable":
            vars_raw.append(elem.attrib["value"])
        for child in childlist:
            get_varlist(child)

    get_varlist(root)
    vars_vals = [
        v.replace(":", "/") if v.startswith("/") == False else v.replace("/:", "")
        for v in vars_raw
    ]
    cust_options.update({"variables": vars_vals})

    return cust_options


# DevGoal: populate this with default variable lists for all of the products!
# DevGoal: add a test for this function (to make sure it returns the right list, but also to deal with product not being in the list, though it should since it was checked as valid earlier...)
def _default_varlists(product):
    """
    Return a list of default variables to select and send to the NSIDC subsetter.
    """
    common_list = ["delta_time", "latitude", "longitude"]

    if product == "ATL06":
        return common_list + [
            "h_li",
            "h_li_sigma",
            "atl06_quality_summary",
            "segment_id",
            "sigma_geo_h",
            "x_atc",
            "y_atc",
            "seg_azimuth",
            "sigma_geo_at",
            "sigma_geo_xt",
            "dh_fit_dx",
            "dh_fit_dx_sigma",
            "h_mean",
            "dh_fit_dy",
            "h_rms_misfit",
            "h_robust_sprd",
            "n_fit_photons",
            "signal_selection_source",
            "snr_significance",
            "w_surface_window_final",
            "bsnow_conf",
            "bsnow_h",
            "cloud_flg_asr",
            "cloud_flg_atm",
            "r_eff",
            "tide_ocean",
        ]

    elif product == "ATL07":
        return common_list + [
            "seg_dist_x",
            "height_segment_height",
            "height_segment_length_seg",
            "height_segment_ssh_flag",
            "height_segment_type",
            "height_segment_quality",
            "height_segment_confidence",
        ]

    elif product == "ATL09":
        return common_list + [
            "bsnow_h",
            "bsnow_dens",
            "bsnow_con",
            "bsnow_psc",
            "bsnow_od",
            "cloud_flag_asr",
            "cloud_fold_flag",
            "cloud_flag_atm",
            "column_od_asr",
            "column_od_asr_qf",
            "layer_attr",
            "layer_bot",
            "layer_top",
            "layer_flag",
            "layer_dens",
            "layer_ib",
            "msw_flag",
            "prof_dist_x",
            "prof_dist_y",
            "apparent_surf_reflec",
        ]

    elif product == "ATL10":
        return common_list + [
            "seg_dist_x",
            "lead_height",
            "lead_length",
            "beam_fb_height",
            "beam_fb_length",
            "beam_fb_confidence",
            "beam_fb_quality_flag",
            "height_segment_height",
            "height_segment_length_seg",
            "height_segment_ssh_flag",
            "height_segment_type",
            "height_segment_confidence",
        ]

    elif product == "ATL11":
        return common_list + [
            "h_corr",
            "h_corr_sigma",
            "h_corr_sigma_systematic",
            "quality_summary",
        ]

    else:
        print(
            "THE REQUESTED PRODUCT DOES NOT YET HAVE A DEFAULT LIST SET UP. ONLY DELTA_TIME, LATITUTDE, AND LONGITUDE WILL BE RETURNED"
        )
        return common_list


def gt2spot(gt, sc_orient):

    assert gt in [
        "gt1l",
        "gt1r",
        "gt2l",
        "gt2r",
        "gt3l",
        "gt3r",
    ], "An invalid ground track was found"

    gr_num = np.uint8(gt[2])
    gr_lr = gt[3]

    if sc_orient == 1:
        if gr_num == 1:
            if gr_lr == "l":
                spot = 2
            elif gr_lr == "r":
                spot = 1
        elif gr_num == 2:
            if gr_lr == "l":
                spot = 4
            elif gr_lr == "r":
                spot = 3
        elif gr_num == 3:
            if gr_lr == "l":
                spot = 6
            elif gr_lr == "r":
                spot = 5

    elif sc_orient == 0:
        if gr_num == 1:
            if gr_lr == "l":
                spot = 5
            elif gr_lr == "r":
                spot = 6
        elif gr_num == 2:
            if gr_lr == "l":
                spot = 3
            elif gr_lr == "r":
                spot = 4
        elif gr_num == 3:
            if gr_lr == "l":
                spot = 1
            elif gr_lr == "r":
                spot = 2

    if "spot" not in locals():
        raise ValueError("Could not compute the spot number.")

    return np.uint8(spot)
