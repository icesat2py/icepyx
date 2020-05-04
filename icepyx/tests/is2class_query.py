from icepyx import is2class as ipd
import pytest
import warnings

def test_CMRparams():
    reg_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
    reg_a.build_CMR_params()
    obs_keys = reg_a.CMRparams.keys()
    exp_keys_all = ['short_name','version','temporal']
    exp_keys_any = ['bounding_box','polygon']
    
    assert all(keys in obs_keys for keys in exp_keys_all)
    assert any(key in obs_keys for key in exp_keys_any)
    
def test_reqconfig_params():
    reg_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
    
    #test for search params
    reg_a.build_reqconfig_params('search')
    obs_keys = reg_a.reqparams.keys()
    exp_keys_all = ['page_size','page_num']    
    assert all(keys in obs_keys for keys in exp_keys_all)

    #test for download params
    reg_a.reqparams=None
    reg_a.build_reqconfig_params('download')
    reg_a.reqparams.update({'token':'','email':''})
    obs_keys = reg_a.reqparams.keys()
    exp_keys_all = ['page_size','page_num','request_mode','token','email','include_meta']
    assert all(keys in obs_keys for keys in exp_keys_all)
    
def test_properties():
    reg_a = ipd.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'],\
                            start_time='03:30:00', end_time='21:30:00', version='2')
    obs_list = [reg_a.dataset, reg_a.dates, reg_a.start_time, reg_a.end_time, reg_a.dataset_version, reg_a.spatial_extent]
    exp_list = ['ATL06',['2019-02-22', '2019-02-28'], '03:30:00', '21:30:00', '002', ['bounding box', [-64, 66, -55, 72]]]
    
    for obs, expected in zip(obs_list,exp_list):
        assert obs == expected

#BestPractices: should do additional properties tests for each potential property type (e.g. spatial extent can have type bounding_box or polygon)    

def test_no_granules_in_search_results():
    ermsg = "Your search returned no results; try different search parameters"
    with pytest.raises(AssertionError, match=ermsg):
        ipd.Icesat2Data('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-20'], version='2').avail_granules()

def test_correct_granule_list_returned():
    reg_a = ipd.Icesat2Data('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='2')
    reg_a.avail_granules()
    obs_grans = [gran['producer_granule_id'] for gran in reg_a.granules]
    exp_grans = ['ATL06_20190221121851_08410203_002_01.h5', 'ATL06_20190222010344_08490205_002_01.h5', 'ATL06_20190225121032_09020203_002_01.h5', 'ATL06_20190226005526_09100205_002_01.h5']
    
    assert set(obs_grans) == set(exp_grans)

        

#check that search results are correct (spatially, temporally, match actually available data)