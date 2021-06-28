import icepyx.core.query.Query as Query


def _parse_data_source(source):
    """
    Determine input source data type (files, directories, or urls)
    """
    assert type(source) == list, "You must enter your inputs as a list."
    assert all(
        type(i) == str for i in source
    ), "One or more of your inputs were not provided as strings."

    source_type = type(source)
    assert source_type


class Read:
    """
    Data object to create and use Intake catalogs to read ICESat-2 data into the specified formats.
    Provides flexiblity for reading nested hdf5 files into common analysis formats.

    Parameters
    ----------
    data_source : list of strings
        List of files to read in.
        May be a list of full file paths, directories, or s3 urls.
        Each file to be included must contain the string "ATL".

    catalog : string, default None
        Full path to an Intake catalog for reading in data.
        If you still need to create a catalog, leave as default.

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
        catalog=None,
    ):

        if data_source == None:
            raise ValueError("Please provide a data source.")

        if catalog:
            print("validate catalog")
            self._catalog_path = catalog

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
