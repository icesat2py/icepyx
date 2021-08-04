from intake.catalog import Catalog

# Need to post on intake's page to see if this would be a useful contribution...
# https://github.com/intake/intake/blob/master/intake/source/utils.py#L216
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
    glob : str
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
    glob = ""
    # prev_field_name = None
    for literal_text, field_name, format_specs, _ in fmt.parse(pattern):
        glob += literal_text
        if field_name and (glob[-1] != "*"):
            try:
                glob += "?" * int(format_specs)
            except ValueError:
                glob += "*"
                # alternatively, you could use bits=utils._get_parts_of_format_string(resolved_string, literal_texts, format_specs)
                # and then use len(bits[i]) to get the length of each format_spec
    # print(glob)
    return glob


def build_catalog(
    data_source,
    path_pattern,
    source_type,
    var_paths=None,
    var_path_params=None,
    **kwargs
):
    """
    Build a general Intake catalog for reading in ICESat-2 data.
    This function is used by the read class object to create catalogs from lists of ICESat-2 variables.

    Parameters
    ----------
    var_paths : str, default None
        Variable paths to load.
        Can include general parameter names, which must be contained within double curly brackets and further
        described in `var_path_params`.
        Default list based on data product of provided files.
        If multiple data products are included in the files, the default list will be for the product of the first file.
        This may result in errors during read-in if all files do not have the same variable paths.

    var_path_params : [dict], default None
        List of dictionaries with a keyword for each parameter name specified in the `var_paths` string.
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

    """
    from intake.catalog.local import LocalCatalogEntry, UserParameter
    import intake_xarray

    import icepyx.core.APIformatting as apifmt

    assert (
        var_paths
    ), "You must enter a variable path or you will not be able to read in any data."

    # generalize this/make it so the [engine] values can be entered as kwargs...
    xarray_kwargs_dict = {"engine": "h5netcdf", "group": var_paths}

    source_args_dict = {
        "urlpath": data_source,
        "path_as_pattern": path_pattern,
        "xarray_kwargs": xarray_kwargs_dict,
    }

    metadata_dict = {"version": 1}

    source_dict = {
        "name": source_type,
        "description": "",
        "driver": "intake_xarray.netcdf.NetCDFSource",  # NOTE: this must be a string or the catalog cannot be imported after saving
        "args": source_args_dict,
    }

    if var_path_params:
        source_dict = apifmt.combine_params(
            source_dict,
            {"parameters": [UserParameter(**params) for params in var_path_params]},
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
