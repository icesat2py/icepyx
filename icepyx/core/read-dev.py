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


all_varpaths = list_of_dict_vals(variables.wanted)
vgrp, paths = Variables.parse_var_list(all_varpaths, tiered=True, tiered_vars=False)
print(list_of_dict_vals(variables.wanted))
print(Variables.parse_var_list(variables.wanted, tiered=False, tiered_vars=False))


def read_granule(
    FILENAME, ATTRIBUTES=False, variables_obj=None, var_dict=None, **kwargs
):
    """
    Reads ICESat-2 data files with configurable variable selection.

    Uses outputs from Variables.parse_var_list() to flexibly select and read
    specific variables from granule files.

    Parameters
    ----------
    FILENAME: str or file-like object
        Full path to ICESat-2 file or an open file object
    ATTRIBUTES: bool, default False
        If True, read and return file, group, and variable attributes
    variables_obj: Variables, optional
        An icepyx.core.variables.Variables object with populated `wanted` attribute.
        If provided, var_dict will be extracted from variables_obj.wanted.
        Either variables_obj or var_dict should be provided.
    var_dict: dict, optional
        Dictionary of variable names (keys) to list of full paths (values),
        as returned by Variables.parse_var_list(tiered=False).
        If not provided, will be extracted from variables_obj.wanted.

    Returns
    -------
    IS2_mds: dict
        Variables organized hierarchically matching HDF5 group structure
    IS2_attrs: dict
        Attributes (if ATTRIBUTES=True), otherwise empty dict
    IS2_beams: list
        Valid ICESat-2 beams available in the file
    """
    # Open the HDF5 file for reading
    if isinstance(FILENAME, io.IOBase):
        fileID = h5py.File(FILENAME, "r")
    else:
        fileID = h5py.File(os.path.expanduser(FILENAME), "r")

    # Output HDF5 file information
    logging.info(fileID.filename)
    logging.info(list(fileID.keys()))

    # Determine which variables to read
    if variables_obj is not None:
        # Extract var_dict from Variables object
        if variables_obj.wanted:
            var_dict_parsed, _ = Variables.parse_var_list(
                list_of_dict_vals(variables_obj.wanted), tiered=False
            )
            var_dict = var_dict_parsed
        else:
            raise ValueError(
                "variables_obj.wanted is empty. Please select variables first."
            )

    if var_dict is None:
        raise ValueError(
            "Must provide either variables_obj with selected variables or "
            "var_dict from Variables.parse_var_list()"
        )

    # allocate python dictionaries for variables and attributes
    IS2_mds = {}
    IS2_attrs = {}

    # read each input beam within the file
    IS2_beams = []
    for gtx in [k for k in fileID if bool(re.match(r"gt\d[lr]", k))]:
        # Check if this beam group exists and has any of the requested variables
        if gtx not in fileID:
            continue

        # Check if beam contains any of the requested variables
        has_data = False
        for var_name, paths in var_dict.items():
            for path in paths:
                if path.startswith(f"{gtx}/"):
                    try:
                        fileID[path]
                        has_data = True
                        break
                    except KeyError:
                        pass
            if has_data:
                break

        if has_data:
            IS2_beams.append(gtx)

    # for each included beam
    for gtx in IS2_beams:
        # Initialize beam-level data structures
        IS2_attrs.setdefault(gtx, {})
        IS2_mds.setdefault(gtx, {})

        # Save beam-level attributes if present
        try:
            for key in ("atlas_beam_type", "atlas_spot_number"):
                if key in fileID[gtx].attrs:
                    IS2_attrs[gtx][key] = fileID[gtx].attrs[key]
        except (KeyError, AttributeError):
            pass

        # Read requested variables for this beam
        for var_name, paths in var_dict.items():
            for full_path in paths:
                if not full_path.startswith(f"{gtx}/"):
                    continue

                try:
                    var_data = fileID[full_path][:]

                    # Parse the group hierarchy from the path
                    # e.g., "gt1l/heights/h_ph" -> groups = ["heights"], var = "h_ph"
                    sub_path = full_path[len(gtx) + 1 :]  # Remove "gtXx/" prefix
                    path_parts = sub_path.split("/")

                    if len(path_parts) == 1:
                        # Top-level variable in beam
                        IS2_mds[gtx][var_name] = var_data
                    else:
                        # Nested variable - reconstruct hierarchy
                        current = IS2_mds[gtx]
                        for group in path_parts[:-1]:
                            if group not in current:
                                current[group] = {}
                            current = current[group]
                        current[var_name] = var_data

                    # Read attributes if requested
                    if ATTRIBUTES:
                        var_attrs = {}
                        try:
                            for att_name, att_val in fileID[full_path].attrs.items():
                                var_attrs[att_name] = att_val

                            # Store attributes in corresponding location
                            current_attr = IS2_attrs[gtx]
                            for group in path_parts[:-1]:
                                if group not in current_attr:
                                    current_attr[group] = {}
                                current_attr = current_attr[group]
                            if var_name not in current_attr:
                                current_attr[var_name] = {}
                            current_attr[var_name] = var_attrs
                        except (KeyError, AttributeError):
                            pass

                except KeyError:
                    logging.warning(
                        "Variable %s not found in file %s", full_path, fileID.filename
                    )
                    continue

        # Read group-level attributes if requested
        if ATTRIBUTES:
            try:
                for att_name, att_val in fileID[gtx].attrs.items():
                    if att_name not in IS2_attrs[gtx]:
                        IS2_attrs[gtx][att_name] = att_val
            except (KeyError, AttributeError):
                pass

    # Read non-beam variables (orbit_info, ancillary_data, etc.)
    for var_name, paths in var_dict.items():
        for full_path in paths:
            # Skip beam-specific variables
            if any(full_path.startswith(f"{beam}/") for beam in IS2_beams):
                continue

            try:
                var_data = fileID[full_path][:]

                # Parse path and build hierarchy
                path_parts = full_path.split("/")

                if len(path_parts) == 1:
                    # Top-level variable
                    IS2_mds[var_name] = var_data
                else:
                    # Nested variable
                    current = IS2_mds
                    for group in path_parts[:-1]:
                        if group not in current:
                            current[group] = {}
                        current = current[group]
                    current[var_name] = var_data

                # Read attributes if requested
                if ATTRIBUTES:
                    var_attrs = {}
                    try:
                        for att_name, att_val in fileID[full_path].attrs.items():
                            var_attrs[att_name] = att_val

                        # Store attributes
                        current_attr = IS2_attrs
                        for group in path_parts[:-1]:
                            if group not in current_attr:
                                current_attr[group] = {}
                            current_attr = current_attr[group]
                        if var_name not in current_attr:
                            current_attr[var_name] = {}
                        current_attr[var_name] = var_attrs
                    except (KeyError, AttributeError):
                        pass

            except KeyError:
                logging.warning(
                    "Variable %s not found in file %s", full_path, fileID.filename
                )
                continue

    # Read group-level attributes for non-beam groups if requested
    if ATTRIBUTES:
        for group_name in ["orbit_info", "ancillary_data"]:
            if group_name in fileID:
                if group_name not in IS2_attrs:
                    IS2_attrs[group_name] = {}
                try:
                    for att_name, att_val in fileID[group_name].attrs.items():
                        if att_name not in IS2_attrs[group_name]:
                            IS2_attrs[group_name][att_name] = att_val
                except (KeyError, AttributeError):
                    pass

    # Closing the HDF5 file
    fileID.close()

    # Return the datasets and variables
    return (IS2_mds, IS2_attrs, IS2_beams)
