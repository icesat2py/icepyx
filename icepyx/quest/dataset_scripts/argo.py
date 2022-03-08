from dataset import DataSet
import requests
import pandas as pd
import os

class Argo(DataSet):

	def __init__(self, boundingbox, timeframe):
		super.__init__(boundingbox, timeframe)
		self.profiles = None


	def search_data(self, presRange=None):
		"""
		query dataset given the spatio temporal criteria
		and other params specic to the dataset
		"""

		# todo: these need to be formatted to satisfy query
		baseURL = 'https://argovis.colorado.edu/selection/profiles/'
		startDateQuery = '?startDate=' + self._start
		endDateQuery = '&endDate=' + self._end
		shapeQuery = '&shape=' + self._spat_extent

		if not presRange == None:
			pressRangeQuery = '&presRange;=' + presRange
			url = baseURL + startDateQuery + endDateQuery + pressRangeQuery + shapeQuery
		else:
			url = baseURL + startDateQuery + endDateQuery + shapeQuery
		resp = requests.get(url)

		# Consider any status other than 2xx an error
		if not resp.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(resp)
		selectionProfiles = resp.json()
		self.profiles = self.parse_into_df(selectionProfiles)

	def parse_into_df(self, profiles):
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
