import warnings

warnings.filterwarnings("ignore")


class DataSet:

    """
    Parent Class for all supported datasets (i.e. ATL03, ATL07, MODIS, etc.)
    all sub classes must support the following methods for use in
    colocated data class
    """

    def __init__(self, boundingbox, timeframe):
        """
        * use existing Icepyx functionality to initialise this
        :param timeframe: datetime
        """
        self.bounding_box = boundingbox
        self.time_frame = timeframe

    def _fmt_coordinates(self):
        # use icepyx geospatial module (icepyx core)
        raise NotImplementedError

    def _fmt_timerange(self):
        """
        will return list of datetime objects [start_time, end_time]
        """
        raise NotImplementedError

    # todo: merge with Icepyx SuperQuery
    def _validate_input(self):
        """
        This may already be done in icepyx.
        Not sure if we need this here
        """
        raise NotImplementedError

    def search_data(self, delta_t):
        """
        query dataset given the spatio temporal criteria
        and other params specic to the dataset
        """
        raise NotImplementedError

    def download(self, out_path):
        """
        once data is querried, the user may choose to dowload the
        data locally
        """
        raise NotImplementedError

    def visualize(self):
        """
        (once data is downloaded)?, makes a quick plot showing where
        data are located
        e.g. Plots location of Argo profile or highlights ATL03 photon track
        """
        raise NotImplementedError

    def _add2colocated_plot(self):
        """
        Takes visualise() functionality and adds the plot to central
        plot with other coincident data. This will be called by
        show_area_overlap() in Colocateddata class
        """
        raise NotImplementedError

    """
    The following are low priority functions
    Not sure these are even worth keeping. Doesn't make sense for 
    all datasets. 
    """

    # def get_meltpond_fraction(self):
    #     raise NotImplementedError
    #
    # def get_sea_ice_fraction(self):
    #     raise NotImplementedError
    #
    # def get_roughness(self):
    #     raise NotImplementedError
