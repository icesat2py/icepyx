import fnmatch
import glob
import os
import xarray as xr

from icepyx.core.query import Query


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


def _validate_source(source):
    """
    Check that the entered data source paths are valid
    """

    # acceptable inputs (for now) are a single file or directory
    assert type(source) == str, "You must enter your input as a string."
    assert (
        os.path.isdir(source) == True or os.path.isfile(source) == True
    ), "Your data source string is not a valid data source."
    return True


def _check_filename_pattern(source, filename_pattern):
    """
    Check that the entered data source file paths match the input filename_pattern
    """
    if os.path.isdir(source):
        filelist = [
            f
            for f in glob.iglob(source, recursive=True)
            if os.path.isfile(f) and fnmatch.fnmatch(f, filename_pattern)
        ]
        print(filelist)
        assert len(filelist) > 0, "None of your filenames match the specified pattern."
        print(
            f"You have {len(filelist)} files matching the filename pattern to be read in."
        )
        return True
    elif os.path.isfile(source):
        assert fnmatch.fnmatch(
            source, filename_pattern
        ), "Your input filename does not match the specified pattern."
        return True
    else:
        return False


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

    filename_pattern : string, default 'ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5'
        String that shows the filename pattern as required for Intake's path_as_pattern argument.
        The default describes files downloaded directly from NSIDC (subsetted and non-subsetted).

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
        filename_pattern=f"ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5",
        catalog=None,
        out_obj_type=xr.Dataset,
    ):

        if data_source == None:
            raise ValueError("Please provide a data source.")
        else:
            assert _validate_source(data_source)
            self.data_source = data_source

        assert _check_filename_pattern(data_source, filename_pattern)
        # Note: need to check if this works for subset and non-subset NSIDC files (processed_ prepends the former)
        # start here with getting an intake path pattern and filename pattern to go from one to the other
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
