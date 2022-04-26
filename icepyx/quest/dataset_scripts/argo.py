from icepyx.quest.dataset_scripts.dataset import DataSet
from icepyx.core.geospatial import geodataframe
import requests
import pandas as pd
import os
import numpy as np

class Argo(DataSet):

	def __init__(self, boundingbox, timeframe):
		super().__init__(boundingbox, timeframe)
		self.profiles = None


	def search_data(self, presRange=None):
		"""
		query dataset given the spatio temporal criteria
		and other params specic to the dataset
		"""

		# todo: these need to be formatted to satisfy query
		baseURL = 'https://argovis.colorado.edu/selection/profiles/'
		startDateQuery = '?startDate=' + self._start.strftime('%Y-%m-%d')
		endDateQuery = '&endDate=' + self._end.strftime('%Y-%m-%d')
		shapeQuery = '&shape=' + self._fmt_coordinates()

		if not presRange == None:
			pressRangeQuery = '&presRange;=' + presRange
			url = baseURL + startDateQuery + endDateQuery + pressRangeQuery + shapeQuery
		else:
			url = baseURL + startDateQuery + endDateQuery + shapeQuery

		payload = {'startDate': self._start.strftime('%Y-%m-%d'),
				   'endDate': self._end.strftime('%Y-%m-%d'),
				   'shape': [self._fmt_coordinates()]}
		resp = requests.get(baseURL, params=payload)
		print(resp.url)

		# resp = requests.get(url)

		# Consider any status other than 2xx an error
		if not resp.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(resp)
		selectionProfiles = resp.json()
		self.profiles = self._parse_into_df(selectionProfiles)

	def _fmt_coordinates(self):
		# todo: make this more robust but for now it works
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
