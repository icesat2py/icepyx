# import icepyx as ipx
import pytest
import warnings
from icepyx.quest import Argo

def test_merge_df():
	reg_a = Argo([-150, 30, -120, 60], ["2022-06-07", "2022-06-14"])
	param_list = ["salinity", "temperature","down_irradiance412"]
	bad_param = ["up_irradiance412"]
	# param_list = ["doxy"]

	# reg_a.search_data(params=bad_param, printURL=True)

	df = reg_a.get_dataframe(params=param_list)
	print(df.columns)
	assert "down_irradiance412" in df.columns
	assert "down_irradiance412_argoqc" in df.columns

	df = reg_a.get_dataframe(["doxy"], keep_existing=True)
	assert "doxy" in df.columns
	assert "doxy_argoqc" in df.columns
	assert "down_irradiance412" in df.columns
	assert "down_irradiance412_argoqc" in df.columns


def test_validate_params():

	bad_param = ["up_irradiance412"]

	error_msg = Argo._validate_params(bad_param)