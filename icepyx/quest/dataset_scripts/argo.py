from icepyx.quest.dataset_scripts.dataset import DataSet
from icepyx.core.geospatial import geodataframe
import requests
import pandas as pd
import os
import numpy as np

class Argo(DataSet):
	"""
	Initialises an Argo Dataset object
	Used to query physical Argo profiles
	-> biogeochemical Argo (BGC) not included

	Examples
    --------
    # example with profiles available
    >>> reg_a = Argo([-154, 30,-143, 37], ['2022-04-12', '2022-04-26'])
	>>> reg_a.search_data()
	>>> print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())
	   pres    temp     lat      lon
	0   3.9  18.608  33.401 -153.913
	1   5.7  18.598  33.401 -153.913
	2   7.7  18.588  33.401 -153.913
	3   9.7  18.462  33.401 -153.913
	4  11.7  18.378  33.401 -153.913

	# example with no profiles
	>>> reg_a = Argo([-55, 68, -48, 71], ['2019-02-20', '2019-02-28'])
	>>> reg_a.search_data()
	Warning: Query returned no profiles
	Please try different search parameters


	See Also
	--------
	DataSet
	GenQuery
	"""
	def __init__(self, boundingbox, timeframe):
		super().__init__(boundingbox, timeframe)
		self.profiles = None


	def search_data(self, presRange=None, printURL=False):
		"""
		query dataset given the spatio temporal criteria
		and other params specific to the dataset
		"""

		# builds URL to be submitted
		baseURL = 'https://argovis.colorado.edu/selection/profiles/'
		payload = {'startDate': self._start.strftime('%Y-%m-%d'),
				   'endDate': self._end.strftime('%Y-%m-%d'),
				   'shape': [self._fmt_coordinates()]}
		if presRange:
			payload['presRange'] = presRange

		# submit request
		resp = requests.get(baseURL, params=payload)

		if printURL:
			print(resp.url)

		# Consider any status other than 2xx an error
		if not resp.status_code // 100 == 2:
			msg = "Error: Unexpected response {}".format(resp)
			print(msg)
			return

		selectionProfiles = resp.json()

		# check for the existence of profiles from query
		if selectionProfiles == []:
			msg = 'Warning: Query returned no profiles\n' \
				  'Please try different search parameters'
			print(msg)
			return

		# if profiles are found, save them to self as dataframe
		self._parse_into_df(selectionProfiles)

	def _fmt_coordinates(self):
		"""
		Convert spatial extent into format needed by argovis
		i.e. list of polygon coords [[[lat1,lon1],[lat2,lon2],...]]
		"""

		gdf = geodataframe(self.extent_type, self._spat_extent)
		coordinates_array = np.asarray(gdf.geometry[0].exterior.coords)
		x = ''
		for i in coordinates_array:
			coord = '[{0},{1}]'.format(i[0], i[1])
			if x == '':
				x = coord
			else:
				x += ','+coord

		x = '[['+ x + ']]'
		return x


	def _parse_into_df(self, profiles):
		"""
		Stores profiles returned by query into dataframe
		saves profiles back to self.profiles
		returns None
		"""
		# initialize dict
		meas_keys = profiles[0]['measurements'][0].keys()
		df = pd.DataFrame(columns=meas_keys)
		for profile in profiles:
			profileDf = pd.DataFrame(profile['measurements'])
			profileDf['cycle_number'] = profile['cycle_number']
			profileDf['profile_id'] = profile['_id']
			profileDf['lat'] = profile['lat']
			profileDf['lon'] = profile['lon']
			profileDf['date'] = profile['date']
			df = pd.concat([df, profileDf], sort=False)
		self.profiles = df

# this is just for the purpose of debugging and should be removed later
if __name__ == '__main__':
	# no search results
	# reg_a = Argo([-55, 68, -48, 71], ['2019-02-20', '2019-02-28'])
	# profiles available
	reg_a = Argo([-154, 30,-143, 37], ['2022-04-12', '2022-04-26'])
	reg_a.search_data()
	print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())
