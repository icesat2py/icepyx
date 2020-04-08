#Generate and format information for submitting to API (general)

#REFACTOR: update this import statement to bring in the formatting functions needed
#lines 31 and below, once they are moved outside of the is2class
from icepyx.core.is2class import Icesat2Data as Icesat2Data

def build_CMR_params(is2obj):
    """
    Build a dictionary of CMR parameter keys to submit for granule searches and download.
    """

    if not hasattr(is2obj,'CMRparams'):
        is2obj.CMRparams={}

    CMR_solo_keys = ['short_name','version','temporal']
    CMR_spat_keys = ['bounding_box','polygon']
    #check to see if the parameter list is already built
    if all(keys in is2obj.CMRparams for keys in CMR_solo_keys) and any(keys in is2obj.CMRparams for keys in CMR_spat_keys):
        pass
    #if not, see which fields need to be added and add them
    else:
        for key in CMR_solo_keys:
            if key in is2obj.CMRparams:
                pass
            else:
                if key == 'short_name':
                    is2obj.CMRparams.update({key:is2obj.dataset})
                elif key == 'version':
                    is2obj.CMRparams.update({key:is2obj._version})
                elif key == 'temporal':
                    is2obj.CMRparams.update(Icesat2Data._fmt_temporal(is2obj._start,is2obj._end,key))
        if any(keys in is2obj.CMRparams for keys in CMR_spat_keys):
            pass
        else:
            is2obj.CMRparams.update(Icesat2Data._fmt_spatial(is2obj.extent_type,is2obj._spat_extent))

def build_reqconfig_params(is2obj,reqtype, **kwargs):
        """
        Build a dictionary of request configuration parameters.
        #DevGoal: Allow updating of the request configuration parameters (right now they must be manually deleted to be modified)
        """

        if not hasattr(is2obj,'reqparams') or is2obj.reqparams==None:
            is2obj.reqparams={}

        if reqtype == 'search':
            reqkeys = ['page_size','page_num']
        elif reqtype == 'download':
            reqkeys = ['page_size','page_num','request_mode','token','email','include_meta']
        else:
            raise ValueError("Invalid request type")

        if all(keys in is2obj.reqparams for keys in reqkeys):
            pass
        else:
            defaults={'page_size':10,'page_num':1,'request_mode':'async','include_meta':'Y'}
            for key in reqkeys:
                if key in kwargs:
                    is2obj.reqparams.update({key:kwargs[key]})
#                 elif key in defaults:
#                     if key is 'page_num':
#                         pnum = math.ceil(len(is2obj.granules)/is2obj.reqparams['page_size'])
#                         if pnum > 0:
#                             is2obj.reqparams.update({key:pnum})
#                         else:
#                             is2obj.reqparams.update({key:defaults[key]})
                elif key in defaults:
                    is2obj.reqparams.update({key:defaults[key]})
                else:
                    pass

        #DevGoal: improve the interfacing with NSIDC/DAAC so it's not paging results
        is2obj.reqparams['page_num'] = 1
        
def build_subset_params(is2obj, **kwargs):
    """
    Build a dictionary of subsetting parameter keys to submit for data orders and download.
    """

    if not hasattr(is2obj,'subsetparams'):
        is2obj.subsetparams={}

    #DevGoal: get list of available subsetting options for the dataset and use this to build appropriate subset parameters
    default_keys = ['time']
    spat_keys = ['bbox','bounding_shape']
    opt_keys = ['format','projection','projection_parameters','Coverage']
    #check to see if the parameter list is already built
    if all(keys in is2obj.subsetparams for keys in default_keys) and (any(keys in is2obj.subsetparams for keys in spat_keys) or hasattr(is2obj, '_geom_filepath')) and all(keys in is2obj.subsetparams for keys in kwargs.keys()):
        pass
    #if not, see which fields need to be added and add them
    else:
        for key in default_keys:
            if key in is2obj.subsetparams:
                pass
            else:
                if key == 'time':
                    is2obj.subsetparams.update(Icesat2Data._fmt_temporal(is2obj._start,is2obj._end, key))
        if any(keys in is2obj.subsetparams for keys in spat_keys) or hasattr(is2obj, '_geom_filepath'):
            pass
        else:
            if is2obj.extent_type == 'bounding_box':
                k = 'bbox'
            elif is2obj.extent_type == 'polygon':
                k = 'bounding_shape'
            is2obj.subsetparams.update(Icesat2Data._fmt_spatial(k,is2obj._spat_extent))
        for key in opt_keys:
            if key == 'Coverage' and key in kwargs:
                #DevGoal: make there be an option along the lines of Coverage=default, which will get the default variables for that dataset without the user having to input is2obj.build_wanted_wanted_var_list as their input value for using the Coverage kwarg
                is2obj.subsetparams.update({key:is2obj._fmt_var_subset_list(kwargs[key])})
            elif key in kwargs:
                is2obj.subsetparams.update({key:kwargs[key]})
            else:
                pass

