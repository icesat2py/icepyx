import warnings
from icepyx.core.query import GenQuery

warnings.filterwarnings("ignore")


class DataSet:

    """
    Template parent class for all QUEST supported datasets (i.e. ICESat-2, Argo BGC, Argo, MODIS, etc.).
    All sub-classes must support the following methods for use via the QUEST class.
    """

    def __init__(self, spatial_extent, date_range, start_time=None, end_time=None):
        """
        Complete any dataset specific initializations (i.e. beyond space and time) required here.
        For instance, ICESat-2 requires a product, and Argo requires parameters.
        One can also check that the "default" space and time supplied by QUEST are the right format
        (e.g. if the spatial extent must be a bounding box).
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Formatting API Inputs

    def _fmt_coordinates(self):
        """
        Convert spatial extent into format needed by DataSet API,
        if different than the formats available directly from SuperQuery.
        """
        raise NotImplementedError

    def _fmt_timerange(self):
        """
        Convert temporal information into format needed by DataSet API,
        if different than the formats available directly from SuperQuery.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Validation

    def _validate_inputs(self):
        """
        Create any additional validation functions for verifying inputs.
        This function is not explicitly called by QUEST,
        but is frequently needed for preparing API requests.

        See Also
        --------
        quest.dataset_scripts.argo.Argo._validate_parameters
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Querying and Getting Data

    def search_data(self):
        """
        Query the dataset (i.e. search for available data)
        given the spatiotemporal criteria and other parameters specific to the dataset.
        """
        raise NotImplementedError

    def download(self):
        """
        Download the data to your local machine.
        """
        raise NotImplementedError

    def save(self, filepath):
        """
        Save the downloaded data to a directory on your local machine.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Working with Data

    def visualize(self):
        """
        Tells QUEST how to plot data (for instance, which parameters to plot) on a basemap.
        For ICESat-2, it might show a photon track, and for Argo it might show a profile location.
        """
        raise NotImplementedError
