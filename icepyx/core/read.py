import fnmatch
import os
import xarray as xr

import icepyx.core.is2cat as is2cat
import icepyx.core.is2ref as is2ref
from icepyx.core.variables import Variables as Variables
from icepyx.core.variables import list_of_dict_vals

# from icepyx.core.query import Query


def _get_datasource_type():  # filepath):
    """
    Determine if the input is from a local system or is an s3 bucket
    Not needed now, but will need to implement for cloud data access
    """

    source_types = ["is2_local", "is2_s3"]
    return source_types[0]

    """
    see Don's code
    use fsspec.get_mapper to determine which kind of file each is;
    determine the first one and then mandate that all items in the list are the same type.
    Could also use: os.path.splitext(f.name)[1].lower() to get file extension

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


def _check_source_for_pattern(source, filename_pattern):
    """
    Check that the entered data source contains files that match the input filename_pattern
    """
    glob_pattern = is2cat._pattern_to_glob(filename_pattern)

    if os.path.isdir(source):
        _, filelist = _run_fast_scandir(source, glob_pattern)
        assert len(filelist) > 0, "None of your filenames match the specified pattern."
        print(
            f"You have {len(filelist)} files matching the filename pattern to be read in."
        )
        return True, filelist
    elif os.path.isfile(source):
        assert fnmatch.fnmatch(
            os.path.basename(source), glob_pattern
        ), "Your input filename does not match the filename pattern."
        return True, [source]
    else:
        return False, None


class Read:
    """
    Data object to create and use Intake catalogs to read ICESat-2 data into the specified formats.
    Provides flexiblity for reading nested hdf5 files into common analysis formats.

    Parameters
    ----------
    data_source : string
        A string with a full file path or full directory path to ICESat-2 hdf5 (.h5) format files.
        Files within a directory must have a consistent filename pattern that includes the "ATL??" data product name.

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
        product=None,
        filename_pattern="ATL{product:2}_{datetime:%Y%m%d%H%M%S}_{rgt:4}{cycle:2}{orbitsegment:2}_{version:3}_{revision:2}.h5",
        catalog=None,
        out_obj_type=None,  # xr.Dataset,
    ):

        if data_source == None:
            raise ValueError("Please provide a data source.")
        else:
            assert _validate_source(data_source)
            self.data_source = data_source

        if product == None:
            raise ValueError(
                "Please provide the ICESat-2 data product of your file(s)."
            )
        else:
            self._prod = is2ref._validate_product(product)

        pattern_ck, filelist = _check_source_for_pattern(data_source, filename_pattern)
        assert pattern_ck
        # Note: need to check if this works for subset and non-subset NSIDC files (processed_ prepends the former)
        self._pattern = filename_pattern
        self._filelist = filelist

        # after validation, use the notebook code and code outline to start implementing the rest of the class
        if catalog:
            assert os.path.isfile(
                catalog
            ), "Your catalog path does not point to a valid file."
            self._catalog_path = catalog

        if out_obj_type:
            print(
                "Output object type will be an xarray DataSet - no other output types are implemented"
            )
        self._out_obj = xr.Dataset

        self._source_type = _get_datasource_type()

    # ----------------------------------------------------------------------
    # Properties

    @property
    def is2catalog(self):
        """
        Print a generic ICESat-2 Intake catalog.
        This catalog does not specify groups, so it cannot be used to read in data.

        Examples
        --------
        >>>
        """
        if not hasattr(self, "_is2catalog") and hasattr(self, "_catalog_path"):
            from intake import open_catalog

            self._is2catalog = open_catalog(self._catalog_path)

        else:
            self._is2catalog = is2cat.build_catalog(
                self.data_source,
                self._pattern,
                self._source_type,
                var_paths="/paths/to/variables",
            )

        return self._is2catalog

    # I cut and pasted this directly out of the Query class - going to need to reconcile the _source/file stuff there

    @property
    def vars(self):
        """
        Return the to read in variables object.
        This instance is generated from the source file or first file in a list of input files (when source is a directory).

        See Also
        --------
        variables.Variables

        Examples
        --------
        >>> reader =
        >>> reader.vars
        <icepyx.core.variables.Variables at [location]>
        """

        if not hasattr(self, "_read_vars"):
            self._read_vars = Variables(
                "file", path=self._filelist[0], product=self._prod
            )

        return self._read_vars

    # ----------------------------------------------------------------------
    # Methods

    def load(self):
        """
        Use a wanted variables list to load the data from the files into memory.
        If you would like to use the Intake catalog you provided to read in a single data variable,
        simply call Intake's `read()` function on the is2catalog property (e.g. `reader.is2catalog.read()`).

        Parameters
        ----------


        """

        # todo:
        # some checks that the file has the required variables?
        # x keep working on example notebook

        # create a dataset for one variable using this method

        # Notes: intake wants an entire group, not an individual variable (which makes sense if we're using its smarts to set up lat, lon, etc)
        # so to get a combined dataset, we need to keep track of beams under the hood, open each group, and then combine them into one xarray where the beams are IDed somehow (or only the strong ones are returned)
        # this means we need to get/track from each dataset we open some of the metadata, which currently isn't brought into the dataset by intake
        # similar to using spots, a question is how well we can "know" this info external to a given granule (e.g. with a table)
        # we should already have functions in vars to separate things out (or can add some) into components, then use that info to iterate according to what the user is asking for

        # actually merge the data into one or more xarray datasets by beam/spot
        # X look at Ben, Tyler, Tian, Shashank, readers to create a reader template and figure out what can be fixed and what the user needs to have control of
        # look into spots and enhancing functionality for more control

        groups_list = list_of_dict_vals(self._read_vars.wanted)
        _, wanted_groups = Variables.parse_var_list(groups_list, tiered=False)
        for var_path in set(wanted_groups):
            if var_path in ["orbit_info", "ancillary_data"]:
                print(var_path + " not read in right now, but will be added")
                # brainstorming: can still use intake to read in these groups, but then just take the variables
                # (which we know from the wanted var list), hold them, and ultimately add them to the ds
                # need to put in a way to return them even if there are no data variables read in in via the else
            else:
                print(var_path)
                varcat = is2cat.build_catalog(
                    self.data_source,
                    self._pattern,
                    self._source_type,
                    var_paths=var_path
                    # var_paths = "/orbit_info"
                    # var_paths = "/{{laser}}/land_ice_segments",
                    # var_path_params = [{"name": "laser",
                    #                     "description": "Laser Beam Number",
                    #                     "type": "str",
                    #                     "default": "gt1l",
                    #                     "allowed": ["gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"]
                    #                 }],
                )

                # print(varcat["is2_local"])
                ds = varcat[self._source_type].read()
                # next step: compute spot and add it as a coordinate...
                # then, add some other functions for manipulating ICESat-2 Xarray stuff, getting rid of the variables the user didn't ask for, etc.,
                # and call those to merge the datasets
                print(ds)

        # how to best iterate through the variables and merge them?
        return ds


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
