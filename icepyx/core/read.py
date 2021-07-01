import fnmatch
import glob
import os
import xarray as xr

import icepyx.core.query.Query as Query


def _get_datasource_type(filepath):
    """
    Determine if the input is from a local system or is an s3 bucket
    Not needed now, but will need to implement for cloud data access
    """
    pass
    """
    see Don's code
    use fsspec.get_mapper to determine which kind of file each is;
    determine the first one and then mandate that all items in the list are the same type.

    If ultimately want to handle mixed types, save the valid paths in a dict with "s3" or "local" as the keys and the list of the files as the values.
    Then the dict can also contain a catalog key with a dict of catalogs for each of those types of inputs ("s3" or "local")
    In general, the issue we'll run into with multiple files is going to be merging during the read in,
    so it could be beneficial to not hide this too much and mandate users handle this intentionally outside the read in itself.
    """


def _validate_source(source, filename_pattern):
    """
    Check that the entered data source paths are valid
    """

    # Start here, with validating the filenames against the pattern (right now this otherwise just checks they're valid inputs twice)

    # acceptable inputs (for now) are a single file or directory with matching filename patterns
    assert type(source) == str, "You must enter your input as a string."
    assert (
        os.path.isdir(source) == True or os.path.isfile(source) == True
    ), "Your data source string is not a valid data source."

    source_path_list = []
    if os.path.isdir(source):
        source_path_list.append(
            [f for f in glob.iglob(source, recursive=True) if os.path.isfile(f)]
        )
    elif os.path.isfile(source):
        source_path_list.append(source)
    else:
        raise ValueError(
            f"{item} does not contain the ATLAS sensor string, 'ATL'. Please use filenames that include ATL."
        )


# after validation, use the notebook code and code outline to start implementing the rest of the class


class Read:
    """
    Data object to create and use Intake catalogs to read ICESat-2 data into the specified formats.
    Provides flexiblity for reading nested hdf5 files into common analysis formats.

    Parameters
    ----------
    data_source : string
        A string with a full file path or full directory path to ICESat-2 hdf5 (.h5) format files.
        Files within a directory must have a consistent filename pattern.

    filename_pattern : string, default 'processed_ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5'
        String that shows the filename pattern.
        The default describes files downloaded directly from NSIDC.

    catalog : string, default None
        Full path to an Intake catalog for reading in data.
        If you still need to create a catalog, leave as default.

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
        filename_pattern=None,
        catalog=None,
        out_obj_type=xr.Dataset,
    ):

        if data_source == None:
            raise ValueError("Please provide a data source.")

        if filename_pattern:
            print("check the filename pattern")
            self._filename_pattern = filename_pattern

        if catalog:
            print("validate catalog")
            self._catalog_path = catalog

        if out_obj_type:
            print("validate data object type")
            self._out_obj = out_obj_type

    # ----------------------------------------------------------------------
    # Properties

    @property
    def catalog(self):
        """
        Print the catalog.

        Examples
        --------
        >>>
        """
        return print(open(self._catalog_path, "r").read())


'''
read.py extra/early dev code

init docstring for using below parse_data_source fn
data_source : list of strings
        List of files to read in.
        May be a list of full file paths, directories, or s3 urls.
        You can combine file paths and directories, but not local files and s3 urls.
        Each file to be included must contain the string "ATL".

def _parse_data_source(source):
    """
    Determine input source data type (files, directories, or urls)
    """
    assert type(source) == list, "You must enter your inputs as a list."
    # DevGoal: accept Path or string inputs and test for validity 
    # (see/modify https://github.com/OSOceanAcoustics/echopype/blob/ab5128fb8580f135d875580f0469e5fba3193b84/echopype/utils/io.py)
    assert all(type(i) == str for i in source), "One or more of your inputs were not provided as strings."
    
    source_path_list = []
    for item in source:
        print(item)
        if os.path.isdir(item):
            source_path_list.append([f for f in glob.iglob(item+'**/*ATL*', recursive=True) if os.path.isfile(f)])
        elif fnmatch.fnmatch(item, "*/*ATL*.*"):
            source_path_list.append(item)
        else:
            raise ValueError(f"{item} does not contain the ATLAS sensor string, 'ATL'. Please use filenames that include ATL.")
        
    
    # source_type = type(source)
    # assert source_type
    return source_path_list


'''
