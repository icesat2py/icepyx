import io
import logging
import os
import re

import h5py

from icepyx.core.variables import Variables as Variables
from icepyx.core.variables import list_of_dict_vals

variables = Variables(product="ATL03")
# AI generated - has not been checked or tested; it does include the mandatory variables from ln 575 of read.py
variables.append(
    keyword_list=["geolocation", "heights", "bckgrd_atlas", "geophys_corr"],
    var_list=[
        "segment_id",
        "reference_photon_lat",
        "reference_photon_lon",
        "ph_index_beg",
        "segment_ph_cnt",
        "segment_dist_x",
        "segment_length",
        "delta_time",
        "ref_elev",
        "ref_azimuth",
        "solar_elevation",
        "solar_azimuth",
        "h_ph",
        "lat_ph",
        "lon_ph",
        "dist_ph_along",
        "dist_ph_across",
        "signal_conf_ph",
        "quality_ph",
        "bckgrd_rate",
        "geoid",
        "sc_orient",
        "atlas_sdp_gps_epoch",
        "cycle_number",
        "rgt",
        "data_start_utc",
        "data_end_utc",
    ],
    beam_list=["gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"],
)

print(list_of_dict_vals(variables.wanted))
print(Variables.parse_var_list(variables.wanted, tiered=False, tiered_vars=False))


def read_granule(FILENAME, ATTRIBUTES=False, **kwargs):
    """
    Reads ICESat-2 ATL03 Global Geolocated Photons data files

    Parameters
    ----------
    FILENAME: str
        full path to ATL03 file
    ATTRIBUTES: bool, default False
        read file, group and variable attributes

    Returns
    -------
    IS2_atl03_mds: dict
        ATL03 variables
    IS2_atl03_attrs: dict
        ATL03 attributes
    IS2_atl03_beams: list
        valid ICESat-2 beams within ATL03 file
    """
    # Open the HDF5 file for reading
    if isinstance(FILENAME, io.IOBase):
        fileID = h5py.File(FILENAME, "r")
    else:
        fileID = h5py.File(os.path.expanduser(FILENAME), "r")

    # Output HDF5 file information
    logging.info(fileID.filename)
    logging.info(list(fileID.keys()))

    # allocate python dictionaries for ICESat-2 ATL03 variables and attributes
    IS2_atl03_mds = {}
    IS2_atl03_attrs = {}

    # read each input beam within the file
    IS2_atl03_beams = []
    for gtx in [k for k in fileID if bool(re.match(r"gt\d[lr]", k))]:
        # check if subsetted beam contains data
        # check in both the geolocation and heights groups
        try:
            fileID[gtx]["geolocation"]["segment_id"]
            fileID[gtx]["heights"]["delta_time"]
        except KeyError:
            pass
        else:
            IS2_atl03_beams.append(gtx)

    # for each included beam
    for gtx in IS2_atl03_beams:
        # -------------------------------------------
        # 1. make sure the beam-level dict exists
        IS2_atl03_attrs.setdefault(gtx, {})
        # 2. always save the two “must-have” attributes
        for key in ("atlas_beam_type", "atlas_spot_number"):
            IS2_atl03_attrs[gtx][key] = fileID[gtx].attrs[key]

        # get each HDF5 variable
        IS2_atl03_mds[gtx] = {}
        IS2_atl03_mds[gtx]["heights"] = {}
        IS2_atl03_mds[gtx]["geolocation"] = {}
        IS2_atl03_mds[gtx]["bckgrd_atlas"] = {}
        IS2_atl03_mds[gtx]["geophys_corr"] = {}
        # ICESat-2 Measurement Group
        for key, val in fileID[gtx]["heights"].items():
            IS2_atl03_mds[gtx]["heights"][key] = val[:]
        # ICESat-2 Geolocation Group
        for key, val in fileID[gtx]["geolocation"].items():
            IS2_atl03_mds[gtx]["geolocation"][key] = val[:]
        # ICESat-2 Background Photon Rate Group
        for key, val in fileID[gtx]["bckgrd_atlas"].items():
            IS2_atl03_mds[gtx]["bckgrd_atlas"][key] = val[:]
        # ICESat-2 Geophysical Corrections Group: Values for tides (ocean,
        # solid earth, pole, load, and equilibrium), inverted barometer (IB)
        # effects, and range corrections for tropospheric delays
        for key, val in fileID[gtx]["geophys_corr"].items():
            IS2_atl03_mds[gtx]["geophys_corr"][key] = val[:]

        # Getting attributes of included variables
        if ATTRIBUTES:
            # Getting attributes of IS2_atl03_mds beam variables
            IS2_atl03_attrs[gtx] = {}
            IS2_atl03_attrs[gtx]["heights"] = {}
            IS2_atl03_attrs[gtx]["geolocation"] = {}
            IS2_atl03_attrs[gtx]["bckgrd_atlas"] = {}
            IS2_atl03_attrs[gtx]["geophys_corr"] = {}

            # Global Group Attributes
            for att_name, att_val in fileID[gtx].attrs.items():
                IS2_atl03_attrs[gtx][att_name] = att_val
            # ICESat-2 Measurement Group
            for key, val in fileID[gtx]["heights"].items():
                IS2_atl03_attrs[gtx]["heights"][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[gtx]["heights"][key][att_name] = att_val
            # ICESat-2 Geolocation Group
            for key, val in fileID[gtx]["geolocation"].items():
                IS2_atl03_attrs[gtx]["geolocation"][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[gtx]["geolocation"][key][att_name] = att_val
            # ICESat-2 Background Photon Rate Group
            for key, val in fileID[gtx]["bckgrd_atlas"].items():
                IS2_atl03_attrs[gtx]["bckgrd_atlas"][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[gtx]["bckgrd_atlas"][key][att_name] = att_val
            # ICESat-2 Geophysical Corrections Group
            for key, val in fileID[gtx]["geophys_corr"].items():
                IS2_atl03_attrs[gtx]["geophys_corr"][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[gtx]["geophys_corr"][key][att_name] = att_val

    # ICESat-2 spacecraft orientation at time
    IS2_atl03_mds["orbit_info"] = {}
    IS2_atl03_attrs["orbit_info"] = {}
    for key, val in fileID["orbit_info"].items():
        IS2_atl03_mds["orbit_info"][key] = val[:]
        # Getting attributes of group and included variables
        if ATTRIBUTES:
            # Global Group Attributes
            for att_name, att_val in fileID["orbit_info"].attrs.items():
                IS2_atl03_attrs["orbit_info"][att_name] = att_val
            # Variable Attributes
            IS2_atl03_attrs["orbit_info"][key] = {}
            for att_name, att_val in val.attrs.items():
                IS2_atl03_attrs["orbit_info"][key][att_name] = att_val

    # information ancillary to the data product
    # number of GPS seconds between the GPS epoch (1980-01-06T00:00:00Z UTC)
    # and ATLAS Standard Data Product (SDP) epoch (2018-01-01T00:00:00Z UTC)
    # Add this value to delta time parameters to compute full gps_seconds
    # could alternatively use the Julian day of the ATLAS SDP epoch: 2458119.5
    # and add leap seconds since 2018-01-01T00:00:00Z UTC (ATLAS SDP epoch)
    IS2_atl03_mds["ancillary_data"] = {}
    IS2_atl03_attrs["ancillary_data"] = {}
    ancillary_keys = [
        "atlas_sdp_gps_epoch",
        "data_end_utc",
        "data_start_utc",
        "end_cycle",
        "end_geoseg",
        "end_gpssow",
        "end_gpsweek",
        "end_orbit",
        "end_region",
        "end_rgt",
        "granule_end_utc",
        "granule_start_utc",
        "release",
        "start_cycle",
        "start_geoseg",
        "start_gpssow",
        "start_gpsweek",
        "start_orbit",
        "start_region",
        "start_rgt",
        "version",
    ]
    for key in ancillary_keys:
        # get each HDF5 variable
        IS2_atl03_mds["ancillary_data"][key] = fileID["ancillary_data"][key][:]
        # Getting attributes of group and included variables
        if ATTRIBUTES:
            # Variable Attributes
            IS2_atl03_attrs["ancillary_data"][key] = {}
            for att_name, att_val in fileID["ancillary_data"][key].attrs.items():
                IS2_atl03_attrs["ancillary_data"][key][att_name] = att_val

    # transmit-echo-path (tep) parameters
    IS2_atl03_mds["ancillary_data"]["tep"] = {}
    IS2_atl03_attrs["ancillary_data"]["tep"] = {}
    for key, val in fileID["ancillary_data"]["tep"].items():
        # get each HDF5 variable
        IS2_atl03_mds["ancillary_data"]["tep"][key] = val[:]
        # Getting attributes of group and included variables
        if ATTRIBUTES:
            # Variable Attributes
            IS2_atl03_attrs["ancillary_data"]["tep"][key] = {}
            for att_name, att_val in val.attrs.items():
                IS2_atl03_attrs["ancillary_data"]["tep"][key][att_name] = att_val

    # channel dead time and first photon bias derived from ATLAS calibration
    cal1, cal2 = ("ancillary_data", "calibrations")
    for var in ["dead_time", "first_photon_bias"]:
        IS2_atl03_mds[cal1][var] = {}
        IS2_atl03_attrs[cal1][var] = {}
        for key, val in fileID[cal1][cal2][var].items():
            # get each HDF5 variable
            if isinstance(val, h5py.Dataset):
                IS2_atl03_mds[cal1][var][key] = val[:]
            elif isinstance(val, h5py.Group):
                IS2_atl03_mds[cal1][var][key] = {}
                for k, v in val.items():
                    IS2_atl03_mds[cal1][var][key][k] = v[:]
            # Getting attributes of group and included variables
            if ATTRIBUTES:
                # Variable Attributes
                IS2_atl03_attrs[cal1][var][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[cal1][var][key][att_name] = att_val
                if isinstance(val, h5py.Group):
                    for k, v in val.items():
                        IS2_atl03_attrs[cal1][var][key][k] = {}
                        for att_name, att_val in val.attrs.items():
                            IS2_atl03_attrs[cal1][var][key][k][att_name] = att_val

    # get ATLAS impulse response variables for the transmitter echo path (TEP)
    tep1, tep2 = ("atlas_impulse_response", "tep_histogram")
    IS2_atl03_mds[tep1] = {}
    IS2_atl03_attrs[tep1] = {}
    for pce in ["pce1_spot1", "pce2_spot3"]:
        IS2_atl03_mds[tep1][pce] = {tep2: {}}
        IS2_atl03_attrs[tep1][pce] = {tep2: {}}
        # for each TEP variable
        for key, val in fileID[tep1][pce][tep2].items():
            IS2_atl03_mds[tep1][pce][tep2][key] = val[:]
            # Getting attributes of included variables
            if ATTRIBUTES:
                # Global Group Attributes
                for att_name, att_val in fileID[tep1][pce][tep2].attrs.items():
                    IS2_atl03_attrs[tep1][pce][tep2][att_name] = att_val
                # Variable Attributes
                IS2_atl03_attrs[tep1][pce][tep2][key] = {}
                for att_name, att_val in val.attrs.items():
                    IS2_atl03_attrs[tep1][pce][tep2][key][att_name] = att_val

    # Global File Attributes
    if ATTRIBUTES:
        for att_name, att_val in fileID.attrs.items():
            IS2_atl03_attrs[att_name] = att_val

    # Closing the HDF5 file
    fileID.close()
    # Return the datasets and variables
    return (IS2_atl03_mds, IS2_atl03_attrs, IS2_atl03_beams)
