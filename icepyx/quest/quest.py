import matplotlib.pyplot as plt

from icepyx.core.query import GenQuery, Query
from icepyx.quest.dataset_scripts.argo import Argo


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

    def add_icesat2(self,
                    product=None,
                    start_time=None,
                    end_time=None,
                    version=None,
                    cycles=None,
                    tracks=None,
                    files=None,
                    **kwargs,
                    ):

        query = Query(product,
                      self._spatial.extent,
                      [self._temporal.start, self._temporal.end],
                      start_time,
                      end_time,
                      version,
                      cycles,
                      tracks,
                      files,
                      **kwargs,
                      )

        self.datasets["icesat2"] = query


    def add_argo(self, params=["temperature"], presRange=None):

        argo = Argo(self._spatial, self._temporal, params, presRange)
        self.datasets["argo"] = argo

    def search_all(self):

        for i in self.datasets.values():
            print()
            if isinstance(i, Query):
                print('icesat2')
                # i.order_granules()
            else:
                print(i)
                msg = i.search_data()

    def download_all(self, path=''):

        for i in self.datasets.values():
            print()
            if isinstance(i, Query):
                print('icesat2')
                # i.download_granules(path)
            else:
                i.download()
                print(i)


    # DEVNOTE: see colocated data branch and phyto team files for code that expands quest functionality

# Todo: remove this later -- just here for debugging
if __name__ == '__main__':
    bounding_box = [-150, 30, -120, 60]
    date_range = ["2022-06-07", "2022-06-14"]
    my_quest = Quest(spatial_extent=bounding_box, date_range=date_range)
    print(my_quest._spatial)
    print(my_quest._temporal)

    my_quest.add_argo(params=["down_irradiance412", "temperature"])
    print(my_quest.datasets["argo"].params)

    my_quest.add_icesat2(product="ATL06")
    print(my_quest.datasets["icesat2"].product)

    print(my_quest)

    print("\nBeginning search...")
    my_quest.search_all()
    print("\nBeginning download...")
    my_quest.download_all()

