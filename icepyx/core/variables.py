
import numpy as np
import os
import pprint

# from icepyx.core.is2class import Icesat2Data as is2d
import icepyx.core.is2ref as is2ref

#DEVGOAL: use h5py to simplify some of these tasks, if possible!

#REFACTOR: class needs better docstrings
class Variables():
    """
    Get, create, interact, and manipulate lists of variables and variable paths
    contained in ICESat-2 datasets.

    Parameters
    ----------
    source : path to directory, list of files, or ICESat-2 data object
        Inputs for the source of variables...
    vartype : string
        One of ['order', 'file'] to indicate the source of the input variables.
        This field will be auto-populated...
    
    Examples
    --------
    >>> 


    """

    def __init__(self, vartype, avail=None, wanted=None, session=None,
                dataset=None, version=None, source=None):#vartype=None):
        
        assert vartype in ['order','file'], "Please submit a valid variables type flag"
        
        self._vartype = vartype
        self.dataset = dataset
        self.avail = avail
        self.wanted = wanted
        self._session = session

        #DevGoal: put some more/robust checks here to assess validity of inputs

        if self._vartype == 'order':
            if self.avail == None:
                self._version = version
        elif self._vartype == 'file':
            #DevGoal: check that the list or string are valid dir/files
            self.source = source
        

    # @property
    # def wanted(self):
    #     return self._wanted

    @staticmethod
    def _parse_var_list(varlist):
        """
        Parse a list of path strings into tiered lists and names of variables
        """

        # create a dictionary of variable names and paths
        vgrp = {}
        num = np.max([v.count('/') for v in varlist])
         #         print('max needed: ' + str(num))
        paths = [[] for i in range(num)]
        
        #print(self._cust_options['variables'])
        for vn in varlist:
            vpath,vkey = os.path.split(vn)
            #print('path '+ vpath + ', key '+vkey)
            if vkey not in vgrp.keys():
                vgrp[vkey] = [vn]
            else:
                vgrp[vkey].append(vn)

            if vpath:
                j=0
                for d in vpath.split('/'):
                        paths[j].append(d)
                        j=j+1
                for i in range(j,num):
                    paths[i].append('none')
                    i=i+1
                    
        return vgrp, paths  

    
    def get_avail(self):
        """
        Get the list of available variables and variable paths from the input dataset

        """

        if self._vartype == 'order':
            if not hasattr(self, 'avail'): self.avail = is2ref._get_custom_options(self._session, self.dataset, self._version)['variables']

        elif self._vartype == 'file':
            pass

    def _check_valid_lists(self, vgrp, allpaths, var_list=None, beam_list=None, keyword_list=None):
        """
        Check that the user is requesting valid paths and/or variables for their dataset.

        See self.append() for further details on the list of input parameters.

        Parameters:
        -----------
        vgrp : dict
            Dictionary containing dataset variables as keys

        allpaths : list
            List of all potential path keywords

        var_list : list of strings, default None
            List of user requested variables

        beam_list : list of strings, default None
            List of user requested beams

        keyword_list : list of strings, default None
            List of user requested variable path keywords

        """
        # check if the list of variables, if specified, are available in the dataset              
        if var_list is not None:
            for var_id in var_list:
                if var_id not in vgrp.keys():
                    err_msg_varid = "Invalid variable name: " + var_id + '. '
                    err_msg_varid = err_msg_varid + 'Please select from this list: '
                    err_msg_varid = err_msg_varid + ', '.join(vgrp.keys())
                    raise ValueError(err_msg_varid)
    
        #DevGoal: is there a way to not have this hard-coded in?
        # check if the list of beams, if specified, are available in the dataset
        if self.dataset=='ATL09':
            beam_avail = ['profile_'+str(i+1) for i in range(3)]
        else:
            beam_avail = ['gt'+str(i+1)+'l' for i in range(3)]
            beam_avail = beam_avail + ['gt'+str(i+1)+'r' for i in range(3)]
        if beam_list is not None:
            for beam_id in beam_list:
                if beam_id not in beam_avail:
                    err_msg_beam = "Invalid beam_id: " + beam_id + '. '
                    err_msg_beam = err_msg_beam + 'Please select from this list: '
                    err_msg_beam = err_msg_beam + ', '.join(beam_avail)
                    raise ValueError(err_msg_beam)

        #check if keywords, if specified, are available for the dataset
        if keyword_list is not None:
            for kw in keyword_list:
#                 assert kw in allpaths, "Invalid keyword. Please select from: " + ', '.join(allpaths)
                if kw not in allpaths:
                    err_msg_kw = "Invalid keyword: " + kw + '. '
                    err_msg_kw = err_msg_kw + 'Please select from this list: '
                    err_msg_kw = err_msg_kw + ', '.join(np.unique(np.array(allpaths)))
                    raise ValueError(err_msg_kw)
 
    
    #DevGoal: we can ultimately add an "interactive" trigger that will open the not-yet-made widget. Otherwise, it will use the var_list passed by the user/defaults
    #DevGoal: we need to re-introduce, if possible, the flexibility to not have all possible variable paths used, eg if the user only wants latitude for profile_1, etc. Right now, they would get all latitude paths and all profile_1 paths. Maybe we can have a inclusive/exclusive boolean trigger?
    #DEVGOAL: we need to be explicit about our handling of existing variables. Does this function append new paths or replace any previously existing list? I think trying to make it so that it can remove paths would be too much, but the former distinction could easily be done with a boolean flag.
    #DevNote: Question: Does it make more sense to set defaults to False. It is likely default vars are only added once, 
    #                   but fine tunes may take more calls to this function. On the other hand, I'd like the function to return some default results withtout input. 
    #DevGoal: actuall implement use of the inclusive flag!
    def append(self, defaults=False, inclusive=False, var_list=None, beam_list=None, keyword_list=None):
        '''
        Add to the list of desired variables using user specified beams and variable list. 
        A pregenerated default variable list can be used by setting defaults to True. 
        Note: The calibrated backscatter cab_prof is not in the default list for ATL09
        
        Parameters:
        -----------
        defaults : boolean, default False
            Include the variables in the default variable list. Defaults are defined per-data product. 
            When specified in conjuction with a var_list, default variables not on the user-
            specified list will be added to the order.

        inclusive : boolean, default True
            Include all variables and variable paths that contain any of the specified variables,
            beams, and keywords. Setting to false will only add variable/beam/path combinations that
            contain values specified. Leaving any input list option set to 'None' will include all
            possible values for that list.
                
        var_list : list of strings, default None
            A list of variables to request, if not all available variables are wanted. 
            A list of available variables can be obtained by entering `var_list=['']` into the function.

        beam_list : list of strings, default None
            A list of beam strings, if only selected beams are wanted (the default value of None will automatically 
            include all beams). For ATL09, acceptable values are ['profile_1', 'profile_2', 'profile_3'].
            For all other datasets, acceptable values are ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r'].

        keyword_list : list of strings, default None
            A list of keywords, from any heirarchy level within the data structure, to select variables within
            the dataset that include that keyword in their path. A list of availble keywords can be obtained by
            entering `keyword_list=['']` into the function.

        Examples:
        ---------
            For ATL07 to add variables related to IS2 beams:
            >>> region_a.build_wanted_var_list(var_list=['latitude'],beam_list=['gt1r'],defaults=True)
            
            To exclude the default variables:
            >>> region_a.build_wanted_var_list(var_list=['latitude'],beam_list=['gt1r'])

            To add additional variables in ancillary_data, orbit_info, or quality_assessment, etc., 
            >>> region_a.build_wanted_var_list(keyword_list=['orbit_info'],var_list=['sc_orient_time'])

            To add all variables in ancillary_data
            >>> region_a.build_wanted_var_list(keyword_list=['ancillary_data'])
        '''

        assert not (defaults==False and var_list==None and beam_list==None and keyword_list==None), \
        "You must enter parameters to add to a variable subset list. If you do not want to subset by variable, ensure your is2.subsetparams dictionary does not contain the key 'Coverage'."
    
        req_vars = {}

        if not hasattr(self, 'avail'): self.get_avail()
        vgrp, paths = self._parse_var_list(self.avail) 
        allpaths = []
        [allpaths.extend(np.unique(np.array(paths[p]))) for p in range(len(paths))]
        allpaths = np.unique(allpaths)

        self._check_valid_lists(vgrp, allpaths, var_list, beam_list, keyword_list)

        #add the mandatory variables to the data object
        nec_varlist = ['sc_orient','atlas_sdp_gps_epoch','data_start_utc','data_end_utc',
                       'granule_start_utc','granule_end_utc','start_delta_time','end_delta_time']

        if not hasattr(self, 'wanted') or self.wanted==None:
            for varid in nec_varlist:
                req_vars[varid] = vgrp[varid]
            self.wanted = req_vars

            #DEVGOAL: add a secondary var list to include uncertainty/error information for lower level data if specific data variables have been specified...

        #generate a list of variable names to include, depending on user input
        sum_varlist = []
        if defaults==True:
            sum_varlist = sum_varlist + is2ref._default_varlists(self.dataset)
        if var_list is not None:
            for vn in var_list:
                if vn not in sum_varlist: sum_varlist.append(vn)
        if len(sum_varlist)==0:
            sum_varlist = vgrp.keys()
        

        #Case only variables (but not keywords or beams) are specified
        if beam_list==None and keyword_list==None:
            for vn in sum_varlist:
                req_vars[vn] = vgrp[vn]
                
        #Case a beam and/or keyword list is specified (with or without variables)
        else:  
            if beam_list==None:
                combined_list = keyword_list
            elif keyword_list==None:
                combined_list = beam_list
            else:
                combined_list = keyword_list + beam_list

            for vkey in sum_varlist:
                for vpath in vgrp[vkey]:
                    vpath_kws = vpath.split('/')
                    
                    if inclusive==True:
                        for kw in combined_list:
                            if kw in vpath_kws:
                                if vkey not in req_vars: req_vars[vkey] = []  
                                if vpath not in req_vars[vkey]: req_vars[vkey].append(vpath)
                    else:
                        try:
                            for bkw in beam_list:
                                if bkw in vpath_kws:
                                    for kw in keyword_list:
                                        if kw in vpath_kws:
                                            if vkey not in req_vars: req_vars[vkey] = []  
                                            if vpath not in req_vars[vkey]: req_vars[vkey].append(vpath)
                        except TypeError:
                            for kw in combined_list:
                                if kw in vpath_kws:
                                    if vkey not in req_vars: req_vars[vkey] = []  
                                    if vpath not in req_vars[vkey]: req_vars[vkey].append(vpath)


                    
                    
                    # for kw in vpath_kws[0:-1]:
                    #     if inclusive==True:
                    #         if (keyword_list is not None and kw in keyword_list) or \
                    #         (beam_list is not None and kw in beam_list):
                    #             if vkey not in req_vars: req_vars[vkey] = []  
                    #             if vpath not in req_vars[vkey]: req_vars[vkey].append(vpath)  
                    #     else:
                    #         if (keyword_list==None and kw in beam_list) or \
                    #             (beam_list==None and kw in keyword_list):
                    #             if vkey not in req_vars: req_vars[vkey] = []  
                    #             if vpath not in req_vars[vkey]: req_vars[vkey].append(vpath)  


                            
        # update the data object variables
        for vkey in req_vars.keys():
            # add all matching keys and paths for new variables
            if vkey not in self.wanted.keys():
                self.wanted[vkey] = req_vars[vkey]
            else:
                for vpath in req_vars[vkey]:
                    if vpath not in self.wanted[vkey]: self.wanted[vkey].append(vpath)
    # print(self.wanted)  
    
    
 #DevGoal: we can ultimately add an "interactive" trigger that will open the not-yet-made widget. Otherwise, it will use the var_list passed by the user/defaults
    #DevGoal: we need to re-introduce, if possible, the flexibility to not have all possible variable paths used, eg if the user only wants latitude for profile_1, etc. Right now, they would get all latitude paths and all profile_1 paths. Maybe we can have a inclusive/exclusive boolean trigger?
    #DEVGOAL: we need to be explicit about our handling of existing variables. Does this function append new paths or replace any previously existing list? I think trying to make it so that it can remove paths would be too much, but the former distinction could easily be done with a boolean flag.
    #DevNote: Question: Does it make more sense to set defaults to False. It is likely default vars are only added once, 
    #                   but fine tunes may take more calls to this function. On the other hand, I'd like the function to return some default results withtout input. 
    def remove(self, all=False, inclusive=False, var_list=None, beam_list=None, keyword_list=None):
        '''
        Remove the variables and paths from the wanted list using user specified beam, keyword,
         and variable lists. 
        
        Parameters:
        -----------
        all : boolean, default False
            Remove all variables and paths from the wanted list.
        
        inclusive : boolean, default True
            Remove all variables and variable paths that contain any of the specified variables,
            beams, and keywords. Setting to false will only add variable/beam/path combinations that
            contain values specified. Leaving any input list option set to 'None' will include all
            possible values for that list.
        
        var_list : list of strings, default None
            A list of variables to request, if not all available variables are wanted. 
            A list of available variables can be obtained by entering `var_list=['']` into the function.

        beam_list : list of strings, default None
            A list of beam strings, if only selected beams are wanted (the default value of None will automatically 
            include all beams). For ATL09, acceptable values are ['profile_1', 'profile_2', 'profile_3'].
            For all other datasets, acceptable values are ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r'].

        keyword_list : list of strings, default None
            A list of keywords, from any heirarchy level within the data structure, to select variables within
            the dataset that include that keyword in their path. A list of availble keywords can be obtained by
            entering `keyword_list=['']` into the function.

        Examples:
        ---------
            For ATL07 to add variables related to IS2 beams:
            >>> region_a.build_wanted_var_list(var_list=['latitude'],beam_list=['gt1r'],defaults=True)
            
            To exclude the default variables:
            >>> region_a.build_wanted_var_list(var_list=['latitude'],beam_list=['gt1r'])

            To add additional variables in ancillary_data, orbit_info, or quality_assessment, etc., 
            >>> region_a.build_wanted_var_list(keyword_list=['orbit_info'],var_list=['sc_orient_time'])

            To add all variables in ancillary_data
            >>> region_a.build_wanted_var_list(keyword_list=['ancillary_data'])
        '''

        if not hasattr(self, 'wanted') or self.wanted==None:
            raise ValueError("You must construct a wanted variable list in order to remove values from it.")

        assert not (all==False and var_list==None and beam_list==None and keyword_list==None), \
        "You must specify which variables/paths/beams you would like to remove from your wanted list."

        req_vars = {}
        
        # if not hasattr(self, 'avail'): self.get_avail()
        # vgrp, paths = self._parse_var_list(self.avail) 
        # # vgrp, paths = self._parse_var_list(self._cust_options['variables']) 
        # allpaths = []
        # [allpaths.extend(np.unique(np.array(paths[p]))) for p in range(len(paths))]
        # allpaths = np.unique(allpaths)

        # self._check_valid_lists(vgrp, allpaths, var_list, beam_list, keyword_list)

        if all==True:
            try: self.wanted=None
            except NameError:
                pass
        
        else:
            #Case only variables (but not keywords or beams) are specified
            if beam_list==None and keyword_list==None:
                for vn in var_list:
                    try: del self.wanted[vn]
                    except KeyError: pass
        
            
            #DevGoal: Do we want to enable the user to remove mandatory variables (how it's written now)?
            #Case a beam and/or keyword list is specified (with or without variables)
            else: 
                if beam_list==None:
                    combined_list = keyword_list
                elif keyword_list==None:
                    combined_list = beam_list
                else:
                    combined_list = keyword_list + beam_list
                
                # nec_varlist = ['sc_orient','atlas_sdp_gps_epoch','data_start_utc','data_end_utc',
                #             'granule_start_utc','granule_end_utc','start_delta_time','end_delta_time']
                for vkey in self.wanted.keys():
                    if inclusive==True:
                        if vkey in var_list:
                            del self.wanted[vkey]
                        else:
                            vpaths = self.wanted[vkey]
                            for vpath in vpaths:
                                vpath_kws = vpath.split('/')
                            
                                for kw in combined_list: 
                                    if kw in vpath_kws:
                                        self.wanted[vkey].remove(vpath)
                                       
                    
                    else:
                        # vpaths = tuple(self.wanted[vkey])
                        for vpath in tuple(self.wanted[vkey]):
                            vpath_kws = vpath.split('/')

                            for kw in combined_list:
                                if kw in vpath_kws and vkey in var_list:
                                    self.wanted[vkey].remove(vpath)
                
                    if len(self.wanted[vkey])==0:
                        del self.wanted[vkey]
                                
