import matplotlib.pyplot as plt

from icepyx.core.query import GenQuery


# todo: implement the subclass inheritance
class Quest(GenQuery):
    """
    QUEST - Query Unify Explore SpatioTemporal - object to query, obtain, and perform basic
    operations on datasets for combined analysis with ICESat-2 data products.
    A new dataset can be added using the `dataset.py` template.
    A list of already supported datasets is available at:
    Expands the icepyx GenQuery superclass.

    See the doc page for GenQuery for details on temporal and spatial input parameters.


    Parameters
    ----------
    projection : proj4 string
            Not yet implemented
            Ex text: a string name of projection to be used for plotting (e.g. 'Mercator', 'NorthPolarStereographic')

    Returns
    -------
    quest object

    Examples
    --------
    Initializing Quest with a bounding box.

    >>> reg_a_bbox = [-55, 68, -48, 71]
    >>> reg_a_dates = ['2019-02-20','2019-02-28']
    >>> reg_a = Quest(spatial_extent=reg_a_bbox, date_range=reg_a_dates)
    >>> print(reg_a)
    Extent type: bounding_box
    Coordinates: [-55.0, 68.0, -48.0, 71.0]
    Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)
    Data sets: None

    # todo: make this work with real datasets
    Add datasets to the quest object.

    >>> reg_a.datasets = {'ATL07':None, 'Argo':None}
    >>> print(reg_a)
    Extent type: bounding_box
    Coordinates: [-55.0, 68.0, -48.0, 71.0]
    Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)
    Data sets: ATL07, Argo

    See Also
    --------
    GenQuery
    """

    def __init__(
        self,
        spatial_extent=None,
        date_range=None,
        start_time=None,
        end_time=None,
        proj="Default",
    ):
        super().__init__(spatial_extent, date_range, start_time, end_time)
        self.datasets = {}
        self.projection = self._determine_proj(proj)

    # todo: maybe move this to icepyx superquery class
    def _determine_proj(self, proj):
        return None

    def __str__(self):
        str = super(Quest, self).__str__()

        str += "\nData sets: "

        if not self.datasets:
            str += "None"
        else:
            for i in self.datasets.keys():
                str += "{0}, ".format(i)
            str = str[:-2]  # remove last ', '

        return str

    # DEVNOTE: see colocated data branch and phyto team files for code that expands quest functionality
