# import icepyx as ipx
import pytest
import warnings
from icepyx.quest import Argo

def test_validate_params():
	reg_a = Argo([-150, 30, -120, 60], ["2022-06-07", "2022-06-14"])
	param_list = ["down_irradiance412"]
	bad_param = ["up_irradiance412"]
	# param_list = ["doxy"]

	# reg_a.search_data(params=bad_param, printURL=True)

	df = reg_a.get_dataframe(params=param_list)
	assert 1==1

def test_abc():
	assert 1 == 1