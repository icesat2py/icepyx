import icepyx as ipx
import pytest
import warnings
from icepyx.quest.dataset_scripts.argo import Argo


def test_available_profiles():
	reg_a = Argo([-154, 30, -143, 37], ['2022-04-12', '2022-04-26'])
	reg_a.search_data()

	assert 'temp' in reg_a.profiles.columns
	print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())

def test_no_available_profiles():
	pass

def test_valid_spatialextent():
	pass

