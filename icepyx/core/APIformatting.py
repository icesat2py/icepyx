#Generate and format information for submitting to API (CMR and NSIDC)

import datetime as dt
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

# ----------------------------------------------------------------------
# parameter-specific formatting for display
# or input to a set of API parameters (CMR or NSIDC)

def _fmt_temporal(start,end,key):
    """
    Format the start and end dates and times into a temporal CMR search 
    or subsetting key value.

    Parameters
    ----------
    start : date time object
        Start date and time for the period of interest.
    end : date time object
        End date and time for the period of interest.
    key : string
        Dictionary key, entered as a string, indicating which temporal format is needed.
        Must be one of ['temporal','time'] for data searching and subsetting, respectively.
    """

    assert isinstance(start, dt.datetime)
    assert isinstance(end, dt.datetime)
    #DevGoal: add test for proper keys
    if key == 'temporal':
        fmt_timerange = start.strftime('%Y-%m-%dT%H:%M:%SZ') +',' + end.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif key == 'time':
        fmt_timerange = start.strftime('%Y-%m-%dT%H:%M:%S') +',' + end.strftime('%Y-%m-%dT%H:%M:%S')

    return {key:fmt_timerange}


def _fmt_spatial(ext_type,extent):
    """
    Format the spatial extent input into a spatial CMR search or subsetting key value.

    Parameters
    ----------
    extent_type : string
        Spatial extent type. Must be one of ['bounding_box', 'polygon'] for data searching
        or one of ['bbox, 'bounding_shape'] for subsetting.
    extent : list
        Spatial extent, with input format dependent on the extent type and search.
        Bounding box (bounding_box, bbox) coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        Polygon (polygon, bounding_shape) coordinates should be provided in decimal degrees as
        [longitude, latitude, longitude2, latitude2... longituden, latituden].
    """

    #CMR keywords: ['bounding_box', 'polygon']
    #subsetting keywords: ['bbox','bounding_shape']
    assert ext_type in ['bounding_box', 'polygon'] or ext_type in ['bbox','bounding_shape'],\
    "Invalid spatial extent type."

    fmt_extent = ','.join(map(str, extent))

    return {ext_type: fmt_extent}


def _fmt_polygon(spatial_extent):
    """
    Formats input spatial file to shapely polygon

    """
    #polygon formatting code borrowed from Amy Steiker's 03_NSIDCDataAccess_Steiker.ipynb demo.
    #DevGoal: use new function geodataframe here?

    gdf = gpd.read_file(spatial_extent)
    #DevGoal: does the below line mandate that only the first polygon will be read? Perhaps we should require files containing only one polygon?
    #RAPHAEL - It only selects the first polygon if there are multiple. Unless we can supply the CMR params with muliple polygon inputs we should probably req a single polygon.
    poly = gdf.iloc[0].geometry
    #Simplify polygon. The larger the tolerance value, the more simplified the polygon. See Bruce Wallin's function to do this
    poly = poly.simplify(0.05, preserve_topology=False)
    poly = orient(poly, sign=1.0)

    #JESSICA - move this into a separate function/CMR formatting piece, since it will need to be used for an input polygon too?
    #Format dictionary to polygon coordinate pairs for CMR polygon filtering
    polygon = (','.join([str(c) for xy in zip(*poly.exterior.coords.xy) for c in xy])).split(",")
    polygon = [float(i) for i in polygon]
    return polygon


def _fmt_var_subset_list(vdict):
    """
    Return the NSIDC-API subsetter formatted coverage string for variable subset request.
    
    Parameters
    ----------
    vdict : dictionary
        Dictionary containing variable names as keys with values containing a list of
        paths to those variables (so each variable key may have multiple paths, e.g. for
        multiple beams)
    """ 
    
    subcover = ''
    for vn in vdict.keys():
        vpaths = vdict[vn]
        for vpath in vpaths: subcover += '/'+vpath+','
        
    return subcover[:-1]


def combine_params(*param_dicts):
    params={}
    for dictionary in param_dicts:
        params.update(dictionary)
    return params


# ----------------------------------------------------------------------
# parameter-list level formatting (e.g. to create)

def build_CMR_params(CMRparams, dataset, version, start, end, extent_type, spatial_extent):
    """
    Build a dictionary of CMR parameter keys to submit for granule searches and download.
    """

    # if not hasattr(is2obj,'CMRparams'):
    #     CMRparams={}

    CMR_solo_keys = ['short_name','version','temporal']
    CMR_spat_keys = ['bounding_box','polygon']
    #check to see if the parameter list is already built
    if all(keys in CMRparams for keys in CMR_solo_keys) and any(keys in CMRparams for keys in CMR_spat_keys):
        pass
    #if not, see which fields need to be added and add them
    else:
        for key in CMR_solo_keys:
            if key in CMRparams:
                pass
            else:
                if key == 'short_name':
                    CMRparams.update({key:dataset})
                elif key == 'version':
                    CMRparams.update({key:version})
                elif key == 'temporal':
                    CMRparams.update(_fmt_temporal(start,end,key))
        if any(keys in CMRparams for keys in CMR_spat_keys):
            pass
        else:
            CMRparams.update(_fmt_spatial(extent_type,spatial_extent))
    
    return CMRparams

def build_reqconfig_params(reqparams,reqtype, **kwargs):
    """
    Build a dictionary of request configuration parameters.
    #DevGoal: Allow updating of the request configuration parameters (right now they must be manually deleted to be modified)
    """

    # if not hasattr(is2obj,'reqparams') or reqparams==None:
    #     reqparams={}

    if reqtype == 'search':
        reqkeys = ['page_size','page_num']
    elif reqtype == 'download':
        reqkeys = ['page_size','page_num','request_mode','token','email','include_meta']
    else:
        raise ValueError("Invalid request type")

    if all(keys in reqparams for keys in reqkeys):
        pass
    else:
        defaults={'page_size':10,'page_num':1,'request_mode':'async','include_meta':'Y'}
        for key in reqkeys:
            if key in kwargs:
                reqparams.update({key:kwargs[key]})
#                 elif key in defaults:
#                     if key is 'page_num':
#                         pnum = math.ceil(len(is2obj.granules)/reqparams['page_size'])
#                         if pnum > 0:
#                             reqparams.update({key:pnum})
#                         else:
#                             reqparams.update({key:defaults[key]})
            elif key in defaults:
                reqparams.update({key:defaults[key]})
            else:
                pass

    #DevGoal: improve the interfacing with NSIDC/DAAC so it's not paging results
    reqparams['page_num'] = 1

    return reqparams
        
def build_subset_params(subsetparams, geom_filepath = None, **kwargs):
    """
    Build a dictionary of subsetting parameter keys to submit for data orders and download.
    """

    # if not hasattr(is2obj,'subsetparams'):
    #     subsetparams={}

    #DevGoal: get list of available subsetting options for the dataset and use this to build appropriate subset parameters
    default_keys = ['time']
    spat_keys = ['bbox','bounding_shape']
    opt_keys = ['format','projection','projection_parameters','Coverage']
    #check to see if the parameter list is already built
    if all(keys in subsetparams for keys in default_keys) and (any(keys in subsetparams for keys in spat_keys) or geom_filepath is not None) and all(keys in subsetparams for keys in kwargs.keys()):
        pass
    #if not, see which fields need to be added and add them
    else:
        for key in default_keys:
            if key in subsetparams:
                pass
            else:
                if key == 'time':
                    subsetparams.update(_fmt_temporal(start, end, key))
        if any(keys in subsetparams for keys in spat_keys) or geom_filepath is not None:
            pass
        else:
            if extent_type == 'bounding_box':
                k = 'bbox'
            elif extent_type == 'polygon':
                k = 'bounding_shape'
            subsetparams.update(_fmt_spatial(k,spatial_extent))
        for key in opt_keys:
            if key == 'Coverage' and key in kwargs:
                #DevGoal: make there be an option along the lines of Coverage=default, which will get the default variables for that dataset without the user having to input is2obj.build_wanted_wanted_var_list as their input value for using the Coverage kwarg
                subsetparams.update({key:_fmt_var_subset_list(kwargs[key])})
            elif key in kwargs:
                subsetparams.update({key:kwargs[key]})
            else:
                pass