from icepyx.quest.dataset_scripts.dataset import DataSet
from icepyx.quest.dataset_scripts.argo import Argo
from icepyx.core.geospatial import geodataframe
import requests
import pandas as pd
import os
import numpy as np


class BGC_Argo(Argo):
	def __init__(self, boundingbox, timeframe):
		super().__init__(boundingbox, timeframe)
		# self.profiles = None

	def _search_data_BGC_helper(self):
		'''
		make request with two params, and identify profiles that contain
		remaining params
		i.e. mandates the intersection of all specified params
		'''
		pass

	def search_data(self, params, presRange=None, printURL=False):
		# todo: this currently assumes user specifies exactly two BGC search
		#  params. Need to iterate should the user provide more than 2, and
		#  accommodate if user supplies only 1 param

		# todo: validate list of user-entered params
		# builds URL to be submitted
		baseURL = 'https://argovis.colorado.edu/selection/bgc_data_selection/'

		# todo: identify which 2 params we specify (ignore physical params)
		# todo: special case if only 1 BGC measurment is specified
		payload = {'startDate': self._start.strftime('%Y-%m-%d'),
				   'endDate': self._end.strftime('%Y-%m-%d'),
				   'shape': [self._fmt_coordinates()],
				   'meas_1':params[0],
				   'meas_2':params[1]}

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

		# todo: if additional BGC params (>2 specified), filter results

		# if profiles are found, save them to self as dataframe
		self._parse_into_df(selectionProfiles)

	def _validate_parameters(self, params):
		'''
		Asserts that user-specified parameters are valid as per the Argovis documentation here:
		https://argovis.colorado.edu/api-docs/#/catalog/get_catalog_bgc_platform_data__platform_number_

		Returns
		-------
		the list of params sorted in the order in which they should be queried (least
		commonly available to most commonly available)
		'''

		# valid params ordered by how commonly they are measured (approx)
		valid_params = {
			'pres':0,
			'temp':1,
			'psal':2,
			'cndx':3,
			'doxy':4,
			'chla':5,
			'cdom':6,
			'nitrate':7,
			'bbp700':8,
			'down_irradiance412':9,
			'down_irradiance442':10,
			'down_irradiance490':11,
			'downwelling_par':12,
		}

		# checks that params are valid
		for i in params:
			assert i in valid_params.keys(), \
				"Parameter '{0}' is not valid. Valid parameters are {1}".format(i, valid_params.keys())

		# sorts params into order in which they should be queried
		params = sorted(params, key= lambda i: valid_params[i], reverse=True)
		return params


	def _parse_into_df(self, profiles):
		"""
		Stores profiles returned by query into dataframe
		saves profiles back to self.profiles
		returns None
		"""
		# todo: check that this makes appropriate BGC cols in the DF
		# initialize dict
		meas_keys = profiles[0]['bgcMeas'][0].keys()
		df = pd.DataFrame(columns=meas_keys)
		for profile in profiles:
			profileDf = pd.DataFrame(profile['bgcMeas'])
			profileDf['cycle_number'] = profile['cycle_number']
			profileDf['profile_id'] = profile['_id']
			profileDf['lat'] = profile['lat']
			profileDf['lon'] = profile['lon']
			profileDf['date'] = profile['date']
			df = pd.concat([df, profileDf], sort=False)
		self.profiles = df

if __name__ == '__main__':
	# no profiles available
	# reg_a = BGC_Argo([-154, 30, -143, 37], ['2022-04-12', '2022-04-26'])
	# 24 profiles available

	reg_a = BGC_Argo([-150, 30, -120, 60], ['2022-06-07', '2022-06-21'])
	# reg_a.search_data(['doxy', 'pres'], printURL=True)
	# print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())

	# reg_a._validate_parameters(['doxy',
	# 		'chla',
	# 		'cdomm',])


	p = reg_a._validate_parameters(['nitrate', 'pres', 'doxy'])
	print(p)
