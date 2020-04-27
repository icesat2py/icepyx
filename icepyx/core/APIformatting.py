#Generate and format information for submitting to API (CMR and NSIDC)

import datetime as dt
import geopandas as gpd
import pprint
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import fiona
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

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
#DevGoal: this could be expanded, similar to the variables class, to provide users with valid options if need be
class Parameters():
    """
    Build and update the parameter lists needed to submit a data order

    Parameters
    ----------
    partype : string
        Type of parameter list. Must be one of ['CMR','required','subset']
    
    wanted : list of strings
        List of wanted keys to format.

    """

    def __init__(self, partype, values={}, reqtype=None):
        
        assert partype in ['CMR','required','subset'], "You need to submit a valid parametery type."
        self.partype = partype
        
        if partype == 'required':
            assert reqtype in ['search','download'], "A valid require parameter type is needed"
        self._reqtype = reqtype
        
        # self._wanted = wanted
        self._fmted_keys = values

        # if wanted == None and values is not None:
        #     self._wanted = values.keys()


    @property
    def poss_keys(self):
        if not hasattr(self,'_poss_keys'):
            self._get_possible_keys()
        
        return self._poss_keys

        # return pprint(self._poss_keys)

    # @property
    # def wanted_keys(self):
    #     if not hasattr(_wanted):
    #         self._wanted = []

    #     return self._wanted
    
    @property
    def fmted_keys(self):
        # if not hasattr(self,'_fmted_keys'):
        #     self._fmted_keys = {}
        
        return self._fmted_keys


    def _get_possible_keys(self):
        
        if self.partype == 'CMR':
            self._poss_keys = {'default': ['short_name','version','temporal'], 'spatial': ['bounding_box','polygon'], 'optional': []}
        elif self.partype == 'required':
            self._poss_keys = {'search': ['page_size','page_num'], 'download': ['page_size','page_num','request_mode','token','email','include_meta']}
        elif self.partype == 'subset':
            self._poss_keys = {'default': ['time'],'spatial': ['bbox','bounding_shape'],'optional': ['format','projection','projection_parameters','Coverage']}


    def _check_valid_keys(self):
        
        # if self._wanted == None:
        #     raise ValueError("No desired parameter list was passed")
        
        if not hasattr(self, '_poss_keys'): self._get_possible_keys()
        
        for key in self._fmted_keys.values():
            assert key in self._poss_keys.values(), "An invalid key was passed"

    
    def check_req_values(self):
        reqkeys = self.poss_keys[self._reqtype]

        if all(keys in self._fmted_keys.keys() for keys in reqkeys):
            assert all(values in self._fmted_keys.values() for keys in reqkeys), "One of your formated parameters is missing a value"
            return True
        else:
            return False

    def check_values(self):
        default_keys = self.poss_keys['default']
    
        spatial_keys = self.poss_keys['spatial']

        if all(keys in self._fmted_keys.keys() for keys in default_keys):
            assert all(values in self._fmted_keys.values() for keys in default_keys), "One of your formated parameters is missing a value"

            #not the most robust check, but better than nothing...
            if any(keys in self._fmted_keys.keys() for keys in spatial_keys):
                assert any(values in self._fmted_keys.values() for keys in default_keys), "One of your formated parameters is missing a value"
                return True
            else: return False
        else:
            return False

    def build_params(self, **kwargs):
        
        if not kwargs: kwargs={}

        if self.partype == 'required':
            if self.check_req_values==True and kwargs=={}: pass
            else:
                reqkeys = self.poss_keys[self._reqtype]
                defaults={'page_size':10,'page_num':1,'request_mode':'async','include_meta':'Y'}
                for key in reqkeys:
                    print(key)
                    if key in kwargs:
                        self._fmted_keys.update({key:kwargs[key]})
        #                 elif key in defaults:
        #                     if key is 'page_num':
        #                         pnum = math.ceil(len(is2obj.granules)/reqparams['page_size'])
        #                         if pnum > 0:
        #                             reqparams.update({key:pnum})
        #                         else:
        #                             reqparams.update({key:defaults[key]})
                    elif key in defaults:
                        self._fmted_keys.update({key:defaults[key]})
                    else:
                        pass

                self._fmted_keys['page_num'] = 1
                print(self._fmted_keys)

        
        else:
            if self.check_values==True and kwargs==None: pass
            else:
                default_keys = self.poss_keys['default']
                spatial_keys = self.poss_keys['spatial']
                opt_keys = self.poss_keys['optional']

                for key in default_keys:
                    if key in self._fmted_keys.values():
                        assert self._fmted_keys[key]
                    else:
                        if key == 'short_name':
                            self._fmted_keys.update({key:kwargs['dataset']})
                        elif key == 'version':
                            self._fmted_keys.update({key:kwargs['version']})
                        elif key == 'temporal' or key == 'time':
                            self._fmted_keys.update(_fmt_temporal(kwargs['start'],kwargs['end'],key))
                
                
                for key in opt_keys:
                    if key == 'Coverage' and key in kwargs.keys():
                #DevGoal: make there be an option along the lines of Coverage=default, which will get the default variables for that dataset without the user having to input is2obj.build_wanted_wanted_var_list as their input value for using the Coverage kwarg
                        self._fmted_keys.update({key:_fmt_var_subset_list(kwargs[key])})
                    elif key in kwargs:
                        self._fmted_keys.update({key:kwargs[key]})
                    else:
                        pass
            

            if self.partype == 'CMR':
                if any(keys in self._fmted_keys for keys in spatial_keys):
                    pass
                else:
                    self._fmted_keys.update(_fmt_spatial(kwargs['extent_type'],kwargs['spatial_extent']))
            
            elif self.partype == 'subset':
                if any(keys in self._fmted_keys for keys in spatial_keys) or not hasattr(kwargs,'geom_filepath'):
                    pass
                else:
                    if kwargs['extent_type'] == 'bounding_box':
                        k = 'bbox'
                    elif kwargs['extent_type'] == 'polygon':
                        k = 'bounding_shape'
                    self._fmted_keys.update.update(_fmt_spatial(k,kwargs['spatial_extent']))
            