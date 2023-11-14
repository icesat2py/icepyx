import fnmatch
import os
import warnings

import numpy as np
import xarray as xr

from icepyx.core.exceptions import DeprecationError
import icepyx.core.is2ref as is2ref
from icepyx.core.variables import Variables as Variables
from icepyx.core.variables import list_of_dict_vals

# from icepyx.core.query import Query


def _make_np_datetime(df, keyword):
    """
    Typecast the specified keyword dimension/coordinate/variable into a numpy datetime object.

    Removes the timezone ('Z') in UTC timestamps in ICESat-2 data.

    Parameters
    ----------
    df : DataFrame
        Dataframe object

    keyword : str
        name of the time variable, coordinate, or dimension

    Outputs
    -------
    DataFrame with timezone removed.

    Example
    -------
    >>> ds = xr.Dataset({"time": ("time_idx", [b'2019-01-11T05:26:31.323722Z'])}, coords={"time_idx": [0]})
    >>> _make_np_datetime(ds, "time")
    <xarray.Dataset>
    Dimensions:   (time_idx: 1)
    Coordinates:
      * time_idx  (time_idx) int64 0
    Data variables:
        time      (time_idx) datetime64[ns] 2019-01-11T05:26:31.323722

    """

    if df[keyword].str.endswith("Z"):
        # manually remove 'Z' from datetime to allow conversion to np.datetime64 object (support for timezones is deprecated and causes a seg fault)
        df.update({keyword: df[keyword].str[:-1].astype(np.datetime64)})

    else:
        df[keyword] = df[keyword].astype(np.datetime64)

    return df


def _get_track_type_str(grp_path) -> (str, str, str):
    """
    Determine whether the product contains ground tracks, pair tracks, or profiles and
    parse the string/label the dimension accordingly.

    Parameters
    ----------
    grp_path : str
        The group path for the ground track, pair track, or profile.

    Returns
    -------
    track_str : str
       The string for the ground track, pair track, or profile of this group
    spot_dim_name : str
        What the dimension should be named in the dataset
    spot_var_name : str
        What the variable should be named in the dataset
    """

    import re

    # e.g. for ATL03, ATL06, etc.
    if re.match(r"gt[1-3]['r','l']", grp_path):
        track_str = re.match(r"gt[1-3]['r','l']", grp_path).group()
        spot_dim_name = "spot"
        spot_var_name = "gt"

    # e.g. for ATL09
    elif re.match(r"profile_[1-3]", grp_path):
        track_str = re.match(r"profile_[1-3]", grp_path).group()
        spot_dim_name = "profile"
        spot_var_name = "prof"

    # e.g. for ATL11
    elif re.match(r"pt[1-3]", grp_path):
        track_str = re.match(r"pt[1-3]", grp_path).group()
        spot_dim_name = "pair_track"
        spot_var_name = "pt"

    return track_str, spot_dim_name, spot_var_name


# Dev note: function fully tested (except else, which don't know how to get to)
def _check_datasource(filepath):
    """
    Determine if the input is from a local system or is an s3 bucket.
    Then, validate the inputs (for those on the local system; s3 sources are not validated currently)
    """

    from pathlib import Path

    import fsspec
    from fsspec.implementations.local import LocalFileSystem

    source_types = ["is2_local", "is2_s3"]

    if not isinstance(filepath, Path) and not isinstance(filepath, str):
        raise TypeError("filepath must be a string or Path")

    fsmap = fsspec.get_mapper(str(filepath))
    output_fs = fsmap.fs

    if "s3" in output_fs.protocol:
        return source_types[1]
    elif isinstance(output_fs, LocalFileSystem):
        assert _validate_source(filepath)
        return source_types[0]
    else:
        raise ValueError("Could not confirm the datasource type.")

    """
    Could also use: os.path.splitext(f.name)[1].lower() to get file extension

    If ultimately want to handle mixed types, save the valid paths in a dict with "s3" or "local" as the keys and the list of the files as the values.
    Then the dict can also contain a catalog key with a dict of catalogs for each of those types of inputs ("s3" or "local")
    In general, the issue we'll run into with multiple files is going to be merging during the read in,
    so it could be beneficial to not hide this too much and mandate users handle this intentionally outside the read in itself.
    
    this function was derived with some of the following resources, based on echopype
    https://github.com/OSOceanAcoustics/echopype/blob/ab5128fb8580f135d875580f0469e5fba3193b84/echopype/utils/io.py

    https://filesystem-spec.readthedocs.io/en/latest/api.html?highlight=get_map#fsspec.spec.AbstractFileSystem.glob

    https://filesystem-spec.readthedocs.io/en/latest/_modules/fsspec/implementations/local.html

    https://github.com/OSOceanAcoustics/echopype/blob/ab5128fb8580f135d875580f0469e5fba3193b84/echopype/convert/api.py#L380

    https://echopype.readthedocs.io/en/stable/convert.html
    """


# Dev note: function fully tested as currently written
def _validate_source(source):
    """
    Check that the entered data source paths on the local file system are valid

    Currently, s3 data source paths are not validated.
    """

    # acceptable inputs (for now) are a single file or directory
    # would ultimately like to make a Path (from pathlib import Path; isinstance(source, Path)) an option
    # see https://github.com/OSOceanAcoustics/echopype/blob/ab5128fb8580f135d875580f0469e5fba3193b84/echopype/utils/io.py#L82
    assert type(source) == str, "You must enter your input as a string."
    assert (
        os.path.isdir(source) == True or os.path.isfile(source) == True
    ), "Your data source string is not a valid data source."
    return True


# Dev Note: function is tested (at least loosely)
def _run_fast_scandir(dir, fn_glob):
    """
    Quickly scan nested directories to get a list of filenames that match the fn_glob string.
    Modified from https://stackoverflow.com/a/59803793/2441026
    (faster than os.walk or glob methods, and allows filename matching in subdirectories).

    Parameters
    ----------
    dir : str
        full path to the input directory

    fn_glob : str
        glob-style filename pattern

    Outputs
    -------
    subfolders : list
        list of strings of all nested subdirectories

    files : list
        list of strings containing full paths to each file matching the filename pattern
    """

    subfolders, files = [], []

    for f in os.scandir(dir):
        if any(f.name.startswith(s) for s in ["__", "."]):
            continue
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if fnmatch.fnmatch(f.name, fn_glob):
                files.append(f.path)

    for dir in list(subfolders):
        sf, f = _run_fast_scandir(dir, fn_glob)
        subfolders.extend(sf)
        files.extend(f)

    return subfolders, files


# Need to post on intake's page to see if this would be a useful contribution...
# https://github.com/intake/intake/blob/0.6.4/intake/source/utils.py#L216
def _pattern_to_glob(pattern):
    """
    Adapted from intake.source.utils.path_to_glob to convert a path as pattern into a glob style path
    that uses the pattern's indicated number of '?' instead of '*' where an int was specified.

    Returns pattern if pattern is not a string.

    Parameters
    ----------
    pattern : str
        Path as pattern optionally containing format_strings

    Returns
    -------
    glob_path : str
        Path with int format strings replaced with the proper number of '?' and '*' otherwise.

    Examples
    --------
    >>> _pattern_to_glob('{year}/{month}/{day}.csv')
    '*/*/*.csv'
    >>> _pattern_to_glob('{year:4}/{month:2}/{day:2}.csv')
    '????/??/??.csv'
    >>> _pattern_to_glob('data/{year:4}{month:02}{day:02}.csv')
    'data/????????.csv'
    >>> _pattern_to_glob('data/*.csv')
    'data/*.csv'
    """
    from string import Formatter

    if not isinstance(pattern, str):
        return pattern

    fmt = Formatter()
    glob_path = ""
    # prev_field_name = None
    for literal_text, field_name, format_specs, _ in fmt.parse(format_string=pattern):
        glob_path += literal_text
        if field_name and (glob_path != "*"):
            try:
                glob_path += "?" * int(format_specs)
            except ValueError:
                glob_path += "*"
                # alternatively, you could use bits=utils._get_parts_of_format_string(resolved_string, literal_texts, format_specs)
                # and then use len(bits[i]) to get the length of each format_spec
    # print(glob_path)
    return glob_path


# To do: test this class and functions therein
class Read:
    """
    Data object to read ICESat-2 data into the specified formats.
    Provides flexiblity for reading nested hdf5 files into common analysis formats.

    Parameters
    ----------
    data_source : string
        A string with a full file path or full directory path to ICESat-2 hdf5 (.h5) format files.
        Files within a directory must have a consistent filename pattern that includes the "ATL??" data product name.
        Files must all be within a single directory.

    product : string
        ICESat-2 data product ID, also known as "short name" (e.g. ATL03).
        Available data products can be found at: https://nsidc.org/data/icesat-2/data-sets

    filename_pattern : string, default 'ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5'
        String that shows the filename pattern as required for Intake's path_as_pattern argument.
        The default describes files downloaded directly from NSIDC (subsetted and non-subsetted) for most products (e.g. ATL06).
        The ATL11 filename pattern from NSIDC is: 'ATL{product:2}_{rgt:4}{orbitsegment:2}_{cycles:4}_{version:3}_{revision:2}.h5'.

    catalog : string, default None
        Full path to an Intake catalog for reading in data.
        If you still need to create a catalog, leave as default.
        **Deprecation warning:** This argument has been depreciated. Please use the data_source argument to pass in valid data.

    out_obj_type : object, default xarray.Dataset
        The desired format for the data to be read in.
        Currently, only xarray.Dataset objects (default) are available.
        Please ask us how to help enable usage of other data objects!

    Returns
    -------
    read object

    Examples
    --------

    """

    # ----------------------------------------------------------------------
    # Constructors

    def __init__(
        self,
        data_source=None,
        product=None,
        filename_pattern="ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5",
        catalog=None,
        out_obj_type=None,  # xr.Dataset,
    ):
        # Raise error for depreciated argument
        if catalog:
            raise DeprecationError(
                "The `catalog` argument has been deprecated and intake is no longer supported. "
                "Please use the `data_source` argument to specify your dataset instead."
            )

        if data_source is None:
            raise ValueError("Please provide a data source.")
        else:
            self._source_type = _check_datasource(data_source)
            self.data_source = data_source

        if product is None:
            raise ValueError(
                "Please provide the ICESat-2 data product of your file(s)."
            )
        else:
            self._prod = is2ref._validate_product(product)
        pattern_ck, filelist = Read._check_source_for_pattern(
            data_source, filename_pattern
        )
        assert pattern_ck
        # Note: need to check if this works for subset and non-subset NSIDC files (processed_ prepends the former)
        self._pattern = filename_pattern

        # this is a first pass at getting rid of mixed product types and warning the user.
        # it takes an approach assuming the product name is in the filename, but needs reworking if we let multiple products be loaded
        # one way to handle this would be bring in the product info during the loading step and fill in product there instead of requiring it from the user
        filtered_filelist = [file for file in filelist if self._prod in file]
        if len(filtered_filelist) == 0:
            warnings.warn(
                "Your filenames do not contain a product identifier (e.g. ATL06). "
                "You will likely need to manually merge your dataframes."
            )
            self._filelist = filelist
        elif len(filtered_filelist) < len(filelist):
            warnings.warn(
                "Some files matching your filename pattern were removed as they were not the specified product."
            )
            self._filelist = filtered_filelist
        else:
            self._filelist = filelist

        # after validation, use the notebook code and code outline to start implementing the rest of the class

        if out_obj_type is not None:
            print(
                "Output object type will be an xarray DataSet - "
                "no other output types are implemented yet"
            )
        self._out_obj = xr.Dataset

    # ----------------------------------------------------------------------
    # Properties

    # I cut and pasted this directly out of the Query class - going to need to reconcile the _source/file stuff there

    @property
    def vars(self):
        """
        Return the variables object associated with the data being read in.
        This instance is generated from the source file or first file in a list of input files (when source is a directory).

        See Also
        --------
        variables.Variables

        Examples
        --------
        >>> reader = ipx.Read(path_root, "ATL06", pattern) # doctest: +SKIP
        >>> reader.vars  # doctest: +SKIP
        <icepyx.core.variables.Variables at [location]>
        """

        if not hasattr(self, "_read_vars"):
            self._read_vars = Variables(
                "file", path=self._filelist[0], product=self._prod
            )

        return self._read_vars

    # ----------------------------------------------------------------------
    # Methods

    @staticmethod
    def _check_source_for_pattern(source, filename_pattern):
        """
        Check that the entered data source contains files that match the input filename_pattern
        """
        glob_pattern = _pattern_to_glob(filename_pattern)

        if os.path.isdir(source):
            _, filelist = _run_fast_scandir(source, glob_pattern)
            assert (
                len(filelist) > 0
            ), "None of your filenames match the specified pattern."
            print(
                f"You have {len(filelist)} files matching the filename pattern to be read in."
            )
            return True, filelist
        elif os.path.isfile(source):
            assert fnmatch.fnmatch(
                os.path.basename(source), glob_pattern
            ), "Your input filename does not match the filename pattern."
            return True, [source]
        elif isinstance(source, str):
            if source.startswith("s3://"):
                return True, [source]
        elif isinstance(source, list):
            if all(source.startswith("s3://")):
                return True, source

        return False, None

    @staticmethod
    def _add_vars_to_ds(is2ds, ds, grp_path, wanted_groups_tiered, wanted_dict):
        """
        Add the new variables in the group to the dataset template.

        Parameters
        ----------
        is2ds : Xarray dataset
            Template dataset to add new variables to.
        ds : Xarray dataset
            Dataset containing the group to add
        grp_path : str
            hdf5 group path read into ds
        wanted_groups_tiered : list of lists
            A list of lists of deconstructed group + variable paths.
            The first list contains the first portion of the group name (between consecutive "/"),
            the second list contains the second portion of the group name, etc.
            "none" is used to fill in where paths are shorter than the longest path.
        wanted_dict : dict
            Dictionary with variable names as keys and a list of group + variable paths containing those variables as values.

        Returns
        -------
        Xarray Dataset with variables from the ds variable group added.
        """

        if grp_path in ["orbit_info", "ancillary_data"]:
            grp_spec_vars = [
                wanted_groups_tiered[-1][i]
                for i, x in enumerate(wanted_groups_tiered[0])
                if (x == grp_path and wanted_groups_tiered[1][i] == "none")
            ]

            for var in grp_spec_vars:
                is2ds = is2ds.assign({var: ("gran_idx", ds[var].data)})

            try:
                rgt = ds["rgt"].values[0]
                cycle = ds["cycle_number"].values[0]
                try:
                    is2ds["gran_idx"] = [np.uint64(f"{rgt:04d}{cycle:02d}")]
                except NameError:
                    import random

                    is2ds["gran_idx"] = [random.randint(800000, 899998)]
                    warnings.warn("Your granule index is made up of random values.")
                    # You must include the orbit/cycle_number and orbit/rgt variables to generate
            except KeyError:
                is2ds["gran_idx"] = [np.nanmax(is2ds["gran_idx"]) - 1]

            if hasattr(is2ds, "data_start_utc"):
                is2ds = _make_np_datetime(is2ds, "data_start_utc")
                is2ds = _make_np_datetime(is2ds, "data_end_utc")

        else:
            track_str, spot_dim_name, spot_var_name = _get_track_type_str(grp_path)

            # get the spot number if relevant
            if spot_dim_name == "spot":
                spot = is2ref.gt2spot(track_str, is2ds.sc_orient.values[0])
            else:
                spot = track_str

            grp_spec_vars = [
                k
                for k, v in wanted_dict.items()
                if any(f"{grp_path}/{k}" in x for x in v)
            ]

            # handle delta_times with 1 or more dimensions
            idx_range = range(0, len(ds.delta_time.data))
            try:
                photon_ids = (
                    idx_range
                    + np.full_like(idx_range, np.max(is2ds.photon_idx), dtype="int64")
                    + 1
                )
            except AttributeError:
                photon_ids = range(0, len(ds.delta_time.data))

            hold_delta_times = ds.delta_time.data
            ds = (
                ds.reset_coords(drop=False)
                .expand_dims(dim=[spot_dim_name, "gran_idx"])
                .assign_coords(
                    {
                        spot_dim_name: (spot_dim_name, [spot]),
                        "delta_time": ("delta_time", photon_ids),
                    }
                )
                .assign({spot_var_name: (("gran_idx", spot_dim_name), [[track_str]])})
                .rename_dims({"delta_time": "photon_idx"})
                .rename({"delta_time": "photon_idx"})
                # .set_index("photon_idx")
            )

            # handle cases where the delta time is 2d due to multiple cycles in that group
            if spot_dim_name == "pair_track" and np.ndim(hold_delta_times) > 1:
                ds = ds.assign_coords(
                    {"delta_time": (("photon_idx", "cycle_number"), hold_delta_times)}
                )
            else:
                ds = ds.assign_coords({"delta_time": ("photon_idx", hold_delta_times)})

            # for ATL11
            if "ref_pt" in ds.coords:
                ds = (
                    ds.drop_indexes(["ref_pt", "photon_idx"])
                    .drop(["ref_pt", "photon_idx"])
                    .swap_dims({"ref_pt": "photon_idx"})
                    .assign_coords(
                        ref_pt=("photon_idx", ds.ref_pt.data),
                        photon_idx=ds.photon_idx.data,
                    )
                )

                # for the subgoups where there is 1d delta time data, make sure that the cycle number is still a coordinate for merging
                try:
                    ds = ds.assign_coords(
                        {
                            "cycle_number": (
                                "photon_idx",
                                ds.cycle_number["photon_idx"].data,
                            )
                        }
                    )
                    ds["cycle_number"] = ds.cycle_number.astype(np.uint8)
                except KeyError:
                    pass

            grp_spec_vars.extend([spot_var_name, "photon_idx"])

            is2ds = is2ds.merge(
                ds[grp_spec_vars], join="outer", combine_attrs="drop_conflicts"
            )

            # re-cast some dtypes to make array smaller
            is2ds[spot_var_name] = is2ds[spot_var_name].astype(str)
            try:
                is2ds[spot_dim_name] = is2ds[spot_dim_name].astype(np.uint8)
            except ValueError:
                pass

        return is2ds, ds[grp_spec_vars]

    @staticmethod
    def _combine_nested_vars(is2ds, ds, grp_path, wanted_dict):
        """
        Add the deeply nested variables to a dataset with appropriate coordinate information.

        Parameters
        ----------
        is2ds : Xarray dataset
            Dataset to add deeply nested variables to.
        ds : Xarray dataset
            Dataset containing improper dimensions for the variables being added
        grp_path : str
            hdf5 group path read into ds
        wanted_dict : dict
            Dictionary with variable names as keys and a list of group + variable paths containing those variables as values.

        Returns
        -------
        Xarray Dataset with variables from the ds variable group added.
        """

        # Dev Goal: improve this type of iterating to minimize amount of looping required. Would a path handling library be useful here?
        grp_spec_vars = [
            k for k, v in wanted_dict.items() if any(f"{grp_path}/{k}" in x for x in v)
        ]

        # # Use this to handle issues specific to group paths that are more nested
        # tiers = len(wanted_groups_tiered)
        # if tiers > 3 and grp_path.count("/") == tiers - 2:
        #     # Handle attribute conflicts that arose from data descriptions during merging
        #     for var in grp_spec_vars:
        #         ds[var].attrs = ds.attrs
        #     for k in ds[var].attrs.keys():
        #         ds.attrs.pop(k)
        #     # warnings.warn(
        #     #     "Due to the number of layers of variable group paths, some attributes have been dropped from your DataSet during merging",
        #     #     UserWarning,
        #     # )

        try:
            is2ds = _make_np_datetime(is2ds, "data_start_utc")
            is2ds = _make_np_datetime(is2ds, "data_end_utc")

        except (AttributeError, KeyError):
            pass

        ds = ds[grp_spec_vars].swap_dims({"delta_time": "photon_idx"})
        is2ds = is2ds.assign(ds)

        return is2ds

    def load(self):
        """
        Create a single Xarray Dataset containing the data from one or more files and/or ground tracks.
        Uses icepyx's ICESat-2 data product awareness and Xarray's `combine_by_coords` function.

        All items in the wanted variables list will be loaded from the files into memory.
        If you do not provide a wanted variables list, a default one will be created for you.
        """

        # todo:
        # some checks that the file has the required variables?
        # maybe give user some options here about merging parameters?
        # add a check that wanted variables exists, and create them with defaults if possible (and let the user know)
        # write tests for the functions!

        # Notes: intake wants an entire group, not an individual variable (which makes sense if we're using its smarts to set up lat, lon, etc)
        # so to get a combined dataset, we need to keep track of spots under the hood, open each group, and then combine them into one xarray where the spots are IDed somehow (or only the strong ones are returned)
        # this means we need to get/track from each dataset we open some of the metadata, which we include as mandatory variables when constructing the wanted list

        try:
            groups_list = list_of_dict_vals(self._read_vars.wanted)
        except AttributeError:
            pass

        all_dss = []
        # DevNote: I'd originally hoped to rely on intake-xarray in order to not have to iterate through the files myself,
        # by providing a generalized url/source in building the catalog.
        # However, this led to errors when I tried to combine two identical datasets because the single dimension was equal.
        # In these situations, xarray recommends manually controlling the merge/concat process yourself.
        # While unlikely to be a broad issue, I've heard of multiple matching timestamps causing issues for combining multiple IS2 datasets.
        for file in self._filelist:
            all_dss.append(
                self._build_single_file_dataset(file, groups_list)
            )  # wanted_groups, vgrp.keys()))

        if len(all_dss) == 1:
            return all_dss[0]
        else:
            try:
                merged_dss = xr.combine_by_coords(all_dss, data_vars="minimal")
                return merged_dss
            except ValueError as ve:
                warnings.warn(
                    "Your inputs could not be automatically merged using "
                    f"xarray.combine_by_coords due to the following error: {ve}\n"
                    "icepyx will return a list of Xarray DataSets (one per granule) "
                    "which you can combine together manually instead",
                    stacklevel=2,
                )
                return all_dss

    def _build_dataset_template(self, file):
        """
        Create the Xarray dataset object templated for the data to be read in.

        It may be possible to expand this function to provide multiple templates.
        """
        # NOTE: use the hdf5 library to grab the attr for the product specifier
        # can ultimately then use it to check against user specified one or merge strategies (or to return a list of ds)

        is2ds = xr.Dataset(
            coords=dict(
                gran_idx=[np.uint64(999999)],
                source_file=(["gran_idx"], [file]),
            ),
            attrs=dict(data_product=self._prod),
        )
        return is2ds

    def _read_single_grp(self, file, grp_path):
        """
        For a given file and variable group path, construct an xarray Dataset.

        Parameters
        ----------
        file : str
            Full path to ICESat-2 data file.
            Currently tested for locally downloaded files; untested but hopefully works for s3 stored cloud files.
        grp_path : str
            Full string to a variable group.
            E.g. 'gt1l/land_ice_segments'

        Returns
        -------
        Xarray dataset with the specified group.

        """

        return xr.open_dataset(
            file,
            group=grp_path,
            engine="h5netcdf",
            backend_kwargs={"phony_dims": "access"},
        )

    def _build_single_file_dataset(self, file, groups_list):
        """
        Create a single xarray dataset with all of the wanted variables/groups from the wanted var list for a single data file/url.

        Parameters
        ----------
        file : str
            Full path to ICESat-2 data file.
            Currently tested for locally downloaded files; untested but hopefully works for s3 stored cloud files.

        groups_list : list of strings
            List of full paths to data variables within the file.
            e.g. ['orbit_info/sc_orient', 'gt1l/land_ice_segments/h_li', 'gt1l/land_ice_segments/latitude', 'gt1l/land_ice_segments/longitude']

        Returns
        -------
        Xarray Dataset
        """
        file_product = self._read_single_grp(file, "/").attrs["identifier_product_type"]
        assert (
            file_product == self._prod
        ), "Your product specification does not match the product specification within your files."
        # I think the below method might NOT read the file into memory as the above might?
        # import h5py
        # with h5py.File(filepath,'r') as h5pt:
        #     prod_id = h5pt.attrs["identifier_product_type"]

        # DEVNOTE: if and elif does not actually apply wanted variable list, and has not been tested for merging multiple files into one ds
        # if a gridded product
        # TODO: all products need to be tested, and quicklook products added or explicitly excluded
        # Level 3b, gridded (netcdf): ATL14, 15, 16, 17, 18, 19, 20, 21
        if self._prod in [
            "ATL14",
            "ATL15",
            "ATL16",
            "ATL17",
            "ATL18",
            "ATL19",
            "ATL20",
            "ATL21",
            "ATL23",
        ]:
            is2ds = xr.open_dataset(file)

        # Level 3b, hdf5: ATL11
        elif self._prod in ["ATL11"]:
            is2ds = self._build_dataset_template(file)

            # returns the wanted groups as a single list of full group path strings
            wanted_dict, wanted_groups = Variables.parse_var_list(
                groups_list, tiered=False
            )
            wanted_groups_set = set(wanted_groups)

            # orbit_info is used automatically as the first group path so the info is available for the rest of the groups
            # wanted_groups_set.remove("orbit_info")
            wanted_groups_set.remove("ancillary_data")
            # Note: the sorting is critical for datasets with highly nested groups
            wanted_groups_list = ["ancillary_data"] + sorted(wanted_groups_set)

            # returns the wanted groups as a list of lists with group path string elements separated
            _, wanted_groups_tiered = Variables.parse_var_list(
                groups_list, tiered=True, tiered_vars=True
            )

            while wanted_groups_list:
                # print(wanted_groups_list)
                grp_path = wanted_groups_list[0]
                wanted_groups_list = wanted_groups_list[1:]
                ds = self._read_single_grp(file, grp_path)
                is2ds, ds = Read._add_vars_to_ds(
                    is2ds, ds, grp_path, wanted_groups_tiered, wanted_dict
                )

            return is2ds

        # Level 2 and 3a Products: ATL03, 06, 07, 08, 09, 10, 12, 13
        else:
            is2ds = self._build_dataset_template(file)

            # returns the wanted groups as a single list of full group path strings
            wanted_dict, wanted_groups = Variables.parse_var_list(
                groups_list, tiered=False
            )
            wanted_groups_set = set(wanted_groups)
            # orbit_info is used automatically as the first group path so the info is available for the rest of the groups
            wanted_groups_set.remove("orbit_info")
            wanted_groups_set.remove("ancillary_data")
            # Note: the sorting is critical for datasets with highly nested groups
            wanted_groups_list = ["orbit_info", "ancillary_data"] + sorted(
                wanted_groups_set
            )
            # returns the wanted groups as a list of lists with group path string elements separated
            _, wanted_groups_tiered = Variables.parse_var_list(
                groups_list, tiered=True, tiered_vars=True
            )

            while wanted_groups_list:
                grp_path = wanted_groups_list[0]
                wanted_groups_list = wanted_groups_list[1:]
                ds = self._read_single_grp(file, grp_path)
                is2ds, ds = Read._add_vars_to_ds(
                    is2ds, ds, grp_path, wanted_groups_tiered, wanted_dict
                )

                # if there are any deeper nested variables, get those so they have actual coordinates and add them
                # this may apply to (at a minimum): ATL08
                if any(grp_path in grp_path2 for grp_path2 in wanted_groups_list):
                    for grp_path2 in wanted_groups_list:
                        if grp_path in grp_path2:
                            sub_ds = self._read_single_grp(file, grp_path2)
                            ds = Read._combine_nested_vars(
                                ds, sub_ds, grp_path2, wanted_dict
                            )
                            wanted_groups_list.remove(grp_path2)
                    is2ds = is2ds.merge(ds, join="outer", combine_attrs="no_conflicts")

        return is2ds
