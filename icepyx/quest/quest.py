# from .dataset_scripts import *
import matplotlib.pyplot as plt

from sys import path

from icepyx.core.query import GenQuery


# from ./dataset_scripts/atl07 import ATL07

# Colocated data is a sub-class if SuperQuery
# todo: implement the subclass inheritance
class Quest(GenQuery):
	'''
	Query Unify Explore SpatioTemporal
	'''

	def __init__(self, spatial_extent=None, date_range=None, start_time=None, end_time=None, proj='Default'):
		'''
		boundingbox: [lon1, lon2, lat1, lat2]
		time_start: datetime object
		time_end: datetime object
		projection: a string name of projection to be used for plotting (e.g. 'Mercator', 'NorthPolarStereographic')

		>>> reg_a_bbox = [-55, 68, -48, 71]
		>>> reg_a_dates = ['2019-02-20','2019-02-28']
		>>> reg_a = Quest(spatial_extent=reg_a_bbox, date_range=reg_a_dates)
		>>> print(reg_a) # doctest: +NORMALIZE_WHITESPACE
		Extent type: bounding_box
		Coordinates: [-55.0, 68.0, -48.0, 71.0]
		Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)
		Data sets: None

		# todo: make this work with real datasets
		>>> reg_a.datasets = {'ATL07':None, 'Argo':None}
		>>> print(reg_a) # doctest: +NORMALIZE_WHITESPACE
		Extent type: bounding_box
		Coordinates: [-55.0, 68.0, -48.0, 71.0]
		Date range: (2019-02-20 00:00:00, 2019-02-28 23:59:59)
		Data sets: ATL07, Argo
		'''
		super().__init__(spatial_extent, date_range, start_time, end_time)
		self.datasets = {}
		self.projection = self._determine_proj(proj)

	# todo: maybe move this to Icepyx superquery class
	def _determine_proj(self, proj):
		return None

	# if proj == 'Default':
	#     # based on the bounding box specified, determine an appropriate projection
	#     if min(self.bounding_box[2], self.bounding_box[3]) > 30:
	#         return 'NorthPolarStereographic'
	#     elif proj == 'NorthPolarStereo':
	#         pass
	#         # todo: check other regions for most appropriate proj
	#         #  ...
	#
	# else:
	#     # todo: check that user entered valid proj name
	#     return proj

	# todo: add projection to str once implemented
	def __str__(self):
		'''
		Returns a string representation of self
		'''

		str = super(Quest, self).__str__()

		str+="\nData sets: "

		if not self.datasets:
			str += 'None'
		else:
			for i in self.datasets.keys():
				str += '{0}, '.format(i)
			str = str[:-2] # remove last ', '

		return str

# def show_area_overlap(self, show_datasets=None, porj='NorthPolarStereo'):
#
#     # todo: initialize the figure
#     # eg. - specify figure properties, and set appropriate proj.
#     # add in things like coast lines, etc.
#     # things that are common to all datasets within the bounding box
#     # below is some sample code
#     # plt.figure(figsize=(8, 8), dpi=600)
#     # ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0))  # choose polar sterographic for projection
#     # ax.coastlines(resolution='50m', color='black', linewidth=1)
#     # ax.set_extent([-180, 180, 60, 90], ccrs.PlateCarree())
#
#     '''
#     in the above sample 'ax' is the handle (pointer/reference to where the
#     figure properties are saved in memory)
#     - we want to pass this reference to each specific dataset so that it
#     can add in the appropriate plot onto the same set of axes
#     '''
#
#     # todo: iterate over each dataset in the instance of colocated data (quest), and add plot to the set of axes
#
#     for i in self.datasets:
#         i._add2colocated_plot()
#
#     plt.show()
#
#     # ds2plot = []
#     # if show_datasets:
#     #     ds2plot = show_datasets
#     # else:
#     #     ds2plot = self.datasets
#     #
#     # # settings for plots that are common to all figures
#     # # ...
#     #
#     # plt.figure(figsize=(8, 8), dpi=600)
#     # if self.projection == 'NorthPolarStereographic':
#     #     ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0))  # choose polar sterographic for projection
#     # elif self.projection == 'Mercator':
#     #     ax = plt.axes(projection=ccrs.Mercator(central_longitude=0))  # choose polar sterographic for projection
#     #
#     # ax.coastlines(resolution='50m', color='black', linewidth=1)
#     #
#     # for i in ds2plot:
#     #     # call individual plot functions from each dataset object
#     #     pass
#     #
#     #
#     # print('This will show all of the data overlapping on the same axes')
#     pass

# def init_dataset(self, dataset_list):
#
#     for i in dataset_list:
#         print('Searching though {0}'.format(i))
#         self._add_dataset(i)
#
#     print('search complete')
#
#
#
# def _add_dataset(self, dataset_name):
#     '''
#     Adds dataset objcet to dataset dictionary
#     '''
#
#     if dataset_name == 'ATL03':
#         self.datasets[dataset_name] = ATL03(self.bounding_box, self.time_frame)
#     elif dataset_name == 'ATL07':
#         self.datasets[dataset_name] = ATL07(self.bounding_box, self.time_frame)
#     else:
#         print('Error: {0} is not a supported dataset'.format(dataset_name))
#         print('Permitted datasets are \n\tATL03, ATL07')

# dat = Quest([1,2,3,4], yesterday, today)
# dat.init_dataset([ATL03])
