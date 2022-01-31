from intake.catalog import Catalog

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


def build_catalog(
    data_source,
    path_pattern,
    source_type,
    grp_paths=None,
    grp_path_params=None,
    extra_engine_kwargs=None,
    **kwargs
):
    """
    Build a general Intake catalog for reading in ICESat-2 data.
    This function is used by the read class object to create catalogs from lists of ICESat-2 variables.

    Parameters
    ----------
    data_source : string
        A string with a full file path or full directory path to ICESat-2 hdf5 (.h5) format files.
        Files within a directory must have a consistent filename pattern that includes the "ATL??" data product name.
        Files must all be within a single directory.

    path_pattern : string
        String that shows the filename pattern as required for Intake's path_as_pattern argument.

    source_type : string
        String to use as the Local Catalog Entry name.

    grp_paths : str, default None
        Variable paths to load.
        Can include general parameter names, which must be contained within double curly brackets and further
        described in `grp_path_params`.
        Default list based on data product of provided files.
        If multiple data products are included in the files, the default list will be for the product of the first file.
        This may result in errors during read-in if all files do not have the same variable paths.

    grp_path_params : [dict], default None
        List of dictionaries with a keyword for each parameter name specified in the `grp_paths` string.
        Each parameter keyword should contain a dictionary with the acceptable keyword-value pairs for the driver being used.

    **kwargs :
        Keyword arguments to be passed through to `intake.catalog.Catalog.from_dict()`.
        Keywords needed to override default inputs include:
            - `source_args_dict` # highest level source information; keys include: "urlpath", "path_as_pattern", driver-specific ("xarray_kwargs" is default)
            - `metadata_dict`
            - `source_dict` # individual source entry  information (default is supplied by data object; "name", "description", "driver", "args")
            - `defaults_dict`  # catalog "name", "description", "metadata", "entries", etc.

    Returns
    -------
    intake.catalog.Catalog object

    See Also
    --------
    read.Read

    """
    from intake.catalog.local import LocalCatalogEntry, UserParameter
    import intake_xarray

    import icepyx.core.APIformatting as apifmt

    assert (
        grp_paths
    ), "You must enter a variable path or you will not be able to read in any data."

    # generalize this/make it so the [engine] values can be entered as kwargs...
    engine_key = "xarray_kwargs"
    xarray_kwargs_dict = {"engine": "h5netcdf", "group": grp_paths}
    if extra_engine_kwargs:
        for key in extra_engine_kwargs.keys():
            xarray_kwargs_dict[key] = extra_engine_kwargs[key]

    source_args_dict = {
        "urlpath": data_source,
        "path_as_pattern": path_pattern,
        engine_key: xarray_kwargs_dict,
    }

    metadata_dict = {"version": 1}

    source_dict = {
        "name": source_type,
        "description": "",
        "driver": "intake_xarray.netcdf.NetCDFSource",  # NOTE: this must be a string or the catalog cannot be imported after saving
        "args": source_args_dict,
    }

    if grp_path_params:
        source_dict = apifmt.combine_params(
            source_dict,
            {"parameters": [UserParameter(**params) for params in grp_path_params]},
        )

        # NOTE: LocalCatalogEntry has some required positional args (name, description, driver)
        # I tried doing this generally with *source_dict after the positional args (instead of as part of the if)
        # but apparently I don't quite get something about passing dicts with * and ** and couldn't make it work
        local_cat_source = {
            source_type: LocalCatalogEntry(
                name=source_dict.pop("name"),
                description=source_dict.pop("description"),
                driver=source_dict.pop("driver"),
                parameters=source_dict.pop("parameters"),
                args=source_dict.pop("args"),
            )
        }

    else:
        local_cat_source = {
            source_type: LocalCatalogEntry(
                name=source_dict.pop("name"),
                description=source_dict.pop("description"),
                driver=source_dict.pop("driver"),
                args=source_dict.pop("args"),
            )
        }

    defaults_dict = {
        "name": "IS2-hdf5-icepyx-intake-catalog",
        "description": "an icepyx-generated catalog for creating local ICESat-2 intake entries",
        "metadata": metadata_dict,
        "entries": local_cat_source,
    }

    build_cat_dict = apifmt.combine_params(defaults_dict, kwargs)

    return Catalog.from_dict(**build_cat_dict)
