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

	def search_data(self, params, presRange=None, printURL=False, keep_all=True):

		assert len(params) != 0, 'One or more BGC measurements must be specified.'

		# API request requires exactly 2 measurement params, duplicate single of necessary
		if len(params) == 1:
			params.append(params[0])

		# validate list of user-entered params, sorts into order to be queried
		params = self._validate_parameters(params)


		# builds URL to be submitted
		baseURL = 'https://argovis.colorado.edu/selection/bgc_data_selection/'

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


		# deterine which profiles contain all specified params
		prof_ids = self._filter_profiles(selectionProfiles, params)

		print('{0} valid profiles have been identified'.format(len(prof_ids)))
		# iterate and download profiles individually
		for i in prof_ids:
			print("processing profile", i)
			self.download_by_profile(i)

		self.profiles.reset_index(inplace=True)

		if not keep_all:
			# drop BGC measurement columns not specified by user
			drop_params = list(set(list(self._valid_BGC_params())[3:]) - set(params))
			qc_params = []
			for i in drop_params:
				qc_params.append(i + '_qc')
			drop_params += qc_params
			self.profiles.drop(columns=drop_params, inplace=True, errors='ignore')

	def _valid_BGC_params(self):
		'''
		This is a list of valid BGC params, stored here to remove redundancy
		They are ordered by how commonly they are measured (approx)
		'''
		params = valid_params = {
			'pres':0,
			'temp':1,
			'psal':2,
			'cndx':3,
			'doxy':4,
			'ph_in_situ_total':5,
			'chla':6,
			'cdom':7,
			'nitrate':8,
			'bbp700':9,
			'down_irradiance412':10,
			'down_irradiance442':11,
			'down_irradiance490':12,
			'down_irradiance380': 13,
			'downwelling_par':14,
		}
		return params

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
		valid_params = self._valid_BGC_params()

		# checks that params are valid
		for i in params:
			assert i in valid_params.keys(), \
				"Parameter '{0}' is not valid. Valid parameters are {1}".format(i, valid_params.keys())

		# sorts params into order in which they should be queried
		params = sorted(params, key= lambda i: valid_params[i], reverse=True)
		return params

	def _filter_profiles(self, profiles, params):
		'''
		from a dictionary of all profiles returned by first API request, remove the
		profiles that do not contain ALL BGC measurements specified by user
		returns a list of profile ID's that contain all necessary BGC params
		'''
		# todo: filter out BGC profiles
		good_profs = []
		for i in profiles:
			bgc_meas = i['bgcMeasKeys']
			check = all(item in bgc_meas for item in params)
			if check:
				good_profs.append(i['_id'])
				# print(i['_id'])

		# profiles = good_profs
		return good_profs

	def download_by_profile(self, profile_number):
		url = 'https://argovis.colorado.edu/catalog/profiles/{}'.format(profile_number)
		resp = requests.get(url)
		# Consider any status other than 2xx an error
		if not resp.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(resp)
		profile = resp.json()
		self._parse_into_df(profile)
		return profile

	def _parse_into_df(self, profiles):
		"""
		Stores profiles returned by query into dataframe
		saves profiles back to self.profiles
		returns None
		"""
		# todo: check that this makes appropriate BGC cols in the DF
		# initialize dict
		# meas_keys = profiles[0]['bgcMeasKeys']
		# df = pd.DataFrame(columns=meas_keys)

		if not isinstance(profiles, list):
			profiles = [profiles]

		# initialise the df (empty or containing previously processed profiles)
		if not self.profiles is None:
			df = self.profiles
		else:
			df = pd.DataFrame()

		for profile in profiles:
			profileDf = pd.DataFrame(profile['bgcMeas'])
			profileDf['cycle_number'] = profile['cycle_number']
			profileDf['profile_id'] = profile['_id']
			profileDf['lat'] = profile['lat']
			profileDf['lon'] = profile['lon']
			profileDf['date'] = profile['date']
			df = pd.concat([df, profileDf], sort=False)
			# if self.profiles is None:
			# 	df = pd.concat([df, profileDf], sort=False)
			# else:
			# 	df = df.merge(profileDf, on='profile_id')
		self.profiles = df

if __name__ == '__main__':
	# no profiles available
	# reg_a = BGC_Argo([-154, 30, -143, 37], ['2022-04-12', '2022-04-26'])
	# 24 profiles available

	reg_a = BGC_Argo([-150, 30, -120, 60], ['2022-06-07', '2022-06-21'])
	# reg_a.search_data(['doxy', 'nitrate', 'down_irradiance412'], printURL=True, keep_all=False)
	reg_a.search_data(['down_irradiance412'], printURL=True, keep_all=False)
	# print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())

	# reg_a.download_by_profile('4903026_101')

	# reg_a._validate_parameters(['doxy',
	# 		'chla',
	# 		'cdomm',])


	# p = reg_a._validate_parameters(['nitrate', 'pres', 'doxy'])
	# print(p)
