#ICESat-2 specific reference functions

def _validate_dataset(dataset):
    """
    Confirm a valid ICESat-2 dataset was specified
    """
    if isinstance(dataset, str):
        dataset = str.upper(dataset)
        assert dataset in ['ATL01','ATL02', 'ATL03', 'ATL04','ATL06', 'ATL07', 'ATL08', 'ATL09', 'ATL10', \
                           'ATL12', 'ATL13'],\
        "Please enter a valid dataset"
    else:
        raise TypeError("Please enter a dataset string")
    return dataset
#DevGoal: See if there's a way to dynamically get this list so it's automatically updated
    
#DevGoal: populate this with default variable lists for all of the datasets!
#DevGoal: add a test for this function (to make sure it returns the right list, but also to deal with dataset not being in the list, though it should since it was checked as valid earlier...)
def _default_varlists(dataset):
    """
    Return a list of default variables to select and send to the NSIDC subsetter.
    """
    common_list = ['delta_time','latitude','longitude']
    
    if dataset == 'ATL09':
        return common_list + ['bsnow_h','bsnow_dens','bsnow_con','bsnow_psc','bsnow_od',
                    'cloud_flag_asr','cloud_fold_flag','cloud_flag_atm',
                    'column_od_asr','column_od_asr_qf',
                    'layer_attr','layer_bot','layer_top','layer_flag','layer_dens','layer_ib',
                    'msw_flag','prof_dist_x','prof_dist_y','apparent_surf_reflec']
    
    if dataset == 'ATL07':
        return common_list + ['seg_dist_x',
                                'height_segment_height','height_segment_length_seg','height_segment_ssh_flag',
                                'height_segment_type', 'height_segment_quality', 'height_segment_confidence' ]
    
    if dataset == 'ATL10':
        return common_list + ['seg_dist_x','lead_height','lead_length',
                                'beam_fb_height', 'beam_fb_length', 'beam_fb_confidence', 'beam_fb_quality_flag',
                                'height_segment_height','height_segment_length_seg','height_segment_ssh_flag',
                                'height_segment_type', 'height_segment_confidence']
