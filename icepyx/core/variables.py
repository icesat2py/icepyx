import numpy as np
import os
import pprint

import icepyx.core.is2ref as is2ref

# DEVGOAL: use h5py to simplify some of these tasks, if possible!


def list_of_dict_vals(input_dict):
    """
    Create a single list of the values from a dictionary.
    """
    wanted_list = []
    [wanted_list.append(val) for vals in input_dict.values() for val in vals]
    return wanted_list


# REFACTOR: class needs better docstrings
# DevNote: currently this class is not tested
class Variables:
    """
    Get, create, interact, and manipulate lists of variables and variable paths
    contained in ICESat-2 products.

    Parameters
    ----------
    vartype : string
        One of ['order', 'file'] to indicate the source of the input variables.
        This field will be auto-populated when a variable object is created as an
        attribute of a query object.
    avail : dictionary, default None
        Dictionary (key:values) of available variable names (keys) and paths (values).
    wanted : dictionary, default None
        As avail, but for the desired list of variables
    session : requests.session object
        A session object authenticating the user to download data using their Earthdata login information.
        The session object will automatically be passed from the query object if you
        have successfully logged in there.
    product : string, default None
        Properly formatted string specifying a valid ICESat-2 product
    version : string, default None
        Properly formatted string specifying a valid version of the ICESat-2 product
    path : string, default None
        For vartype file, a path to a directory of or single input data file (not yet implemented)
    """

    def __init__(
        self,
        vartype,
        avail=None,
        wanted=None,
        session=None,
        product=None,
        version=None,
        path=None,
    ):

        assert vartype in ["order", "file"], "Please submit a valid variables type flag"

        self._vartype = vartype
        self.product = product
        self._avail = avail
        self.wanted = wanted
        self._session = session

        # DevGoal: put some more/robust checks here to assess validity of inputs

        if self._vartype == "order":
            if self._avail == None:
                self._version = version
        elif self._vartype == "file":
            # DevGoal: check that the list or string are valid dir/files
            self.path = path

    # @property
    # def wanted(self):
    #     return self._wanted

    def avail(self, options=False, internal=False):
        """
        Get the list of available variables and variable paths from the input data product

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='1')
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> reg_a.order_vars.avail()
        ['ancillary_data/atlas_sdp_gps_epoch',
        'ancillary_data/control',
        'ancillary_data/data_end_utc',
        'ancillary_data/data_start_utc',
        .
        .
        .
        'quality_assessment/gt3r/signal_selection_source_fraction_3']
        """
        # if hasattr(self, '_avail'):
        #         return self._avail
        # else:
        if not hasattr(self, "_avail") or self._avail == None:
            if self._vartype == "order":
                self._avail = is2ref._get_custom_options(
                    self._session, self.product, self._version
                )["variables"]

            elif self._vartype == "file":
                import h5py

                self._avail = []

                def visitor_func(name, node):
                    if isinstance(node, h5py.Group):
                        # node is a Group
                        pass
                    else:
                        # node is a Dataset
                        self._avail.append(name)

                with h5py.File(self.path, "r") as h5f:
                    h5f.visititems(visitor_func)

        if options == True:
            vgrp, paths = self.parse_var_list(self._avail)
            allpaths = []
            [allpaths.extend(np.unique(np.array(paths[p]))) for p in range(len(paths))]
            allpaths = np.unique(allpaths)
            if internal == False:
                print("var_list inputs: " + ", ".join(vgrp.keys()))
                print("keyword_list and beam_list inputs: " + ", ".join(allpaths))
            elif internal == True:
                return vgrp, allpaths
        else:
            return self._avail

    @staticmethod
    def parse_var_list(varlist, tiered=True):
        """
        Parse a list of path strings into tiered lists and names of variables

        Parameters
        ----------
        varlist : list of strings
            List of full variable paths to be parsed.

        tiered : boolean, default True
            Whether to return the paths (sans variable name) as a nested list of component strings
            (e.g. [['orbit_info', 'ancillary_data', 'gt1l'],['none','none','land_ice_segments']])
            or a single list of path strings (e.g. ['orbit_info','ancillary_data','gt1l/land_ice_segments'])

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'], version='1')
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········
        >>> var_dict, paths = reg_a.order_vars.parse_var_list(reg_a.order_vars.avail())
        >>> var_dict
        {'atlas_sdp_gps_epoch': ['ancillary_data/atlas_sdp_gps_epoch'],
        .
        .
        .
        'latitude': ['gt1l/land_ice_segments/latitude',
        'gt1r/land_ice_segments/latitude',
        'gt2l/land_ice_segments/latitude',
        'gt2r/land_ice_segments/latitude',
        'gt3l/land_ice_segments/latitude',
        'gt3r/land_ice_segments/latitude'],
        .
        .
        .
        }
        >>> var_dict.keys()
        dict_keys(['atlas_sdp_gps_epoch', 'control', 'data_end_utc', 'data_start_utc',
        'end_cycle', 'end_delta_time', 'end_geoseg', 'end_gpssow', 'end_gpsweek',
        'end_orbit', 'end_region', 'end_rgt', 'granule_end_utc', 'granule_start_utc',
        'qa_at_interval', 'release', 'start_cycle', 'start_delta_time', 'start_geoseg',
        'start_gpssow', 'start_gpsweek', 'start_orbit', 'start_region', 'start_rgt',
        'version', 'dt_hist', 'fit_maxiter', 'fpb_maxiter', 'maxiter', 'max_res_ids',
        'min_dist', 'min_gain_th', 'min_n_pe', 'min_n_sel', 'min_signal_conf', 'n_hist',
        'nhist_bins', 'n_sigmas', 'proc_interval', 'qs_lim_bsc', 'qs_lim_hrs', 'qs_lim_hsigma',
        'qs_lim_msw', 'qs_lim_snr', 'qs_lim_sss', 'rbin_width', 'sigma_beam', 'sigma_tx',
        't_dead', 'atl06_quality_summary', 'delta_time', 'h_li', 'h_li_sigma', 'latitude',
        'longitude', 'segment_id', 'sigma_geo_h', 'fpb_mean_corr', 'fpb_mean_corr_sigma',
        'fpb_med_corr', 'fpb_med_corr_sigma', 'fpb_n_corr', 'med_r_fit', 'tx_mean_corr',
        tx_med_corr', 'dem_flag', 'dem_h', 'geoid_h', 'dh_fit_dx', 'dh_fit_dx_sigma', '
        dh_fit_dy', 'h_expected_rms', 'h_mean', 'h_rms_misfit', 'h_robust_sprd',
        'n_fit_photons', 'n_seg_pulses', 'sigma_h_mean', 'signal_selection_source',
        'signal_selection_source_status', 'snr', 'snr_significance', 'w_surface_window_final',
        ckgrd', 'bsnow_conf', 'bsnow_h', 'bsnow_od', 'cloud_flg_asr', 'cloud_flg_atm', 'dac',
        'e_bckgrd', 'layer_flag', 'msw_flag', 'neutat_delay_total', 'r_eff', 'solar_azimuth',
        'solar_elevation', 'tide_earth', 'tide_equilibrium', 'tide_load', 'tide_ocean',
        'tide_pole', 'ref_azimuth', 'ref_coelv', 'seg_azimuth', 'sigma_geo_at', 'sigma_geo_r',
        igma_geo_xt', 'x_atc', 'y_atc', 'bckgrd_per_m', 'bin_top_h', 'count', 'ds_segment_id',
        'lat_mean', 'lon_mean', 'pulse_count', 'segment_id_list', 'x_atc_mean', 'record_number',
        'reference_pt_lat', 'reference_pt_lon', 'signal_selection_status_all',
        'signal_selection_status_backup', 'signal_selection_status_confident', 'crossing_time',
        'cycle_number', 'lan', 'orbit_number', 'rgt', 'sc_orient', 'sc_orient_time',
        'qa_granule_fail_reason', 'qa_granule_pass_fail', 'signal_selection_source_fraction_0',
        'signal_selection_source_fraction_1', 'signal_selection_source_fraction_2',
        'signal_selection_source_fraction_3'])
        >>> import numpy
        >>> numpy.unique(paths)
        array(['ancillary_data', 'bias_correction', 'dem', 'fit_statistics',
        'geophysical', 'ground_track', 'gt1l', 'gt1r', 'gt2l', 'gt2r',
        'gt3l', 'gt3r', 'land_ice', 'land_ice_segments', 'none',
        'orbit_info', 'quality_assessment', 'residual_histogram',
        'segment_quality', 'signal_selection_status'], dtype='<U23')
        """

        # create a dictionary of variable names and paths
        vgrp = {}
        if tiered == False:
            paths = []
        else:
            num = np.max([v.count("/") for v in varlist])
            #         print('max needed: ' + str(num))
            paths = [[] for i in range(num)]

        # print(self._cust_options['variables'])
        for vn in varlist:
            vpath, vkey = os.path.split(vn)
            # print('path '+ vpath + ', key '+vkey)
            if vkey not in vgrp.keys():
                vgrp[vkey] = [vn]
            else:
                vgrp[vkey].append(vn)

            if vpath:
                if tiered == False:
                    paths.append(vpath)
                else:
                    j = 0
                    for d in vpath.split("/"):
                        paths[j].append(d)
                        j = j + 1
                    for i in range(j, num):
                        paths[i].append("none")
                        i = i + 1

        return vgrp, paths

    def _check_valid_lists(
        self, vgrp, allpaths, var_list=None, beam_list=None, keyword_list=None
    ):
        """
        Check that the user is requesting valid paths and/or variables for their product.

        See self.append() for further details on the list of input parameters.

        Parameters:
        -----------
        vgrp : dict
            Dictionary containing product variables as keys

        allpaths : list
            List of all potential path keywords

        var_list : list of strings, default None
            List of user requested variables

        beam_list : list of strings, default None
            List of user requested beams

        keyword_list : list of strings, default None
            List of user requested variable path keywords

        """
        # check if the list of variables, if specified, are available in the product
        if var_list is not None:
            for var_id in var_list:
                if var_id not in vgrp.keys():
                    err_msg_varid = "Invalid variable name: " + var_id + ". "
                    err_msg_varid = err_msg_varid + "Please select from this list: "
                    err_msg_varid = err_msg_varid + ", ".join(vgrp.keys())
                    raise ValueError(err_msg_varid)

        # DevGoal: is there a way to not have this hard-coded in?
        # check if the list of beams, if specified, are available in the product
        if self.product == "ATL09":
            beam_avail = ["profile_" + str(i + 1) for i in range(3)]
        else:
            beam_avail = ["gt" + str(i + 1) + "l" for i in range(3)]
            beam_avail = beam_avail + ["gt" + str(i + 1) + "r" for i in range(3)]
        if beam_list is not None:
            for beam_id in beam_list:
                if beam_id not in beam_avail:
                    err_msg_beam = "Invalid beam_id: " + beam_id + ". "
                    err_msg_beam = err_msg_beam + "Please select from this list: "
                    err_msg_beam = err_msg_beam + ", ".join(beam_avail)
                    raise ValueError(err_msg_beam)

        # check if keywords, if specified, are available for the product
        if keyword_list is not None:
            for kw in keyword_list:
                #                 assert kw in allpaths, "Invalid keyword. Please select from: " + ', '.join(allpaths)

                # DevGoal: update here to not include profiles/beams in the allpaths list
                if kw not in allpaths:
                    err_msg_kw = "Invalid keyword: " + kw + ". "
                    err_msg_kw = err_msg_kw + "Please select from this list: "
                    err_msg_kw = err_msg_kw + ", ".join(np.unique(np.array(allpaths)))
                    raise ValueError(err_msg_kw)

    def _get_sum_varlist(self, var_list, all_vars, defaults):
        """
        Get the list of variables to add or iterate through, depending on function inputs.
        """
        sum_varlist = []
        if defaults == True:
            sum_varlist = sum_varlist + is2ref._default_varlists(self.product)
        if var_list is not None:
            for vn in var_list:
                if vn not in sum_varlist:
                    sum_varlist.append(vn)
        if len(sum_varlist) == 0:
            sum_varlist = all_vars

        return sum_varlist

    @staticmethod
    def _get_combined_list(beam_list, keyword_list):
        """
        Get the combined list of beams and/or keywords to add or iterate through.
        """
        combined_list = []
        if beam_list == None:
            combined_list = keyword_list
        elif keyword_list == None:
            combined_list = beam_list
        else:
            combined_list = keyword_list + beam_list

        return combined_list

    @staticmethod
    def _iter_vars(sum_varlist, req_vars, vgrp):
        """
        Iterate through the wanted variables supplied in sum_varlist and add them and their paths
        to the list of requested variables.
        """
        for vn in sum_varlist:
            req_vars[vn] = vgrp[vn]
        return req_vars

    def _iter_paths(self, sum_varlist, req_vars, vgrp, beam_list, keyword_list):
        """
        Iterate through the list of paths for each variable in sum_varlist. Add the paths that have matches
        to combined_list the dictionary of requested variables.
        """
        combined_list = self._get_combined_list(beam_list, keyword_list)

        for vkey in sum_varlist:
            for vpath in vgrp[vkey]:
                vpath_kws = vpath.split("/")

                try:
                    for bkw in beam_list:
                        if bkw in vpath_kws:
                            for kw in keyword_list:
                                if kw in vpath_kws:
                                    if vkey not in req_vars:
                                        req_vars[vkey] = []
                                    if vpath not in req_vars[vkey]:
                                        req_vars[vkey].append(vpath)
                except TypeError:
                    for kw in combined_list:
                        if kw in vpath_kws:
                            if vkey not in req_vars:
                                req_vars[vkey] = []
                            if vpath not in req_vars[vkey]:
                                req_vars[vkey].append(vpath)
        return req_vars

    # DevGoal: we can ultimately add an "interactive" trigger that will open the not-yet-made widget. Otherwise, it will use the var_list passed by the user/defaults
    def append(self, defaults=False, var_list=None, beam_list=None, keyword_list=None):
        """
        Add to the list of desired variables using user specified beams and variable list.
        A pregenerated default variable list can be used by setting defaults to True.
        Note: The calibrated backscatter cab_prof is not in the default list for ATL09

        Parameters
        ----------
        defaults : boolean, default False
            Include the variables in the default variable list. Defaults are defined per-data product.
            When specified in conjuction with a var_list, default variables not on the user-
            specified list will be added to the order.

        var_list : list of strings, default None
            A list of variables to request, if not all available variables are wanted.
            A list of available variables can be obtained by entering `var_list=['']` into the function.

        beam_list : list of strings, default None
            A list of beam strings, if only selected beams are wanted (the default value of None will automatically
            include all beams). For ATL09, acceptable values are ['profile_1', 'profile_2', 'profile_3'].
            For all other products, acceptable values are ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r'].

        keyword_list : list of strings, default None
            A list of subdirectory names (keywords), from any heirarchy level within the data structure, to select variables within
            the product that include that keyword in their path. A list of availble keywords can be obtained by
            entering `keyword_list=['']` into the function.

        Notes
        -----
        See also the `ICESat-2_DAAC_DataAccess2_Subsetting
        <https://github.com/icesat2py/icepyx/blob/main/doc/examples/ICESat-2_DAAC_DataAccess2_Subsetting.ipynb>`_
        example notebook

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········

        To add all variables related to a specific ICESat-2 beam

        >>> reg_a.order_vars.append(beam_list=['gt1r'])

        To include the default variables:

        >>> reg_a.order_vars.append(defaults=True)

        To add specific variables in orbit_info

        >>> reg_a.order_vars.append(keyword_list=['orbit_info'],var_list=['sc_orient_time'])

        To add all variables and paths in ancillary_data

        >>> reg_a.order_vars.append(keyword_list=['ancillary_data'])
        """

        assert not (
            defaults == False
            and var_list == None
            and beam_list == None
            and keyword_list == None
        ), "You must enter parameters to add to a variable subset list. If you do not want to subset by variable, ensure your is2.subsetparams dictionary does not contain the key 'Coverage'."

        req_vars = {}

        # if not hasattr(self, 'avail') or self.avail==None: self.get_avail()
        # vgrp, paths = self.parse_var_list(self.avail)
        # allpaths = []
        # [allpaths.extend(np.unique(np.array(paths[p]))) for p in range(len(paths))]
        vgrp, allpaths = self.avail(options=True, internal=True)

        self._check_valid_lists(vgrp, allpaths, var_list, beam_list, keyword_list)

        # add the mandatory variables to the data object
        if self._vartype == "order":
            nec_varlist = [
                "sc_orient",
                "sc_orient_time",
                "atlas_sdp_gps_epoch",
                "data_start_utc",
                "data_end_utc",
                "granule_start_utc",
                "granule_end_utc",
                "start_delta_time",
                "end_delta_time",
            ]
        elif self._vartype == "file":
            nec_varlist = [
                "sc_orient",
                "atlas_sdp_gps_epoch",
                "cycle_number",
                "rgt",
                "data_start_utc",
                "data_end_utc",
            ]

        if not hasattr(self, "wanted") or self.wanted == None:
            for varid in nec_varlist:
                req_vars[varid] = vgrp[varid]
            self.wanted = req_vars

            # DEVGOAL: add a secondary var list to include uncertainty/error information for lower level data if specific data variables have been specified...

        # generate a list of variable names to include, depending on user input
        sum_varlist = self._get_sum_varlist(var_list, vgrp.keys(), defaults)

        # Case only variables (but not keywords or beams) are specified
        if beam_list == None and keyword_list == None:
            req_vars.update(self._iter_vars(sum_varlist, req_vars, vgrp))

        # Case a beam and/or keyword list is specified (with or without variables)
        else:
            req_vars.update(
                self._iter_paths(sum_varlist, req_vars, vgrp, beam_list, keyword_list)
            )

        # update the data object variables
        for vkey in req_vars.keys():
            # add all matching keys and paths for new variables
            if vkey not in self.wanted.keys():
                self.wanted[vkey] = req_vars[vkey]
            else:
                for vpath in req_vars[vkey]:
                    if vpath not in self.wanted[vkey]:
                        self.wanted[vkey].append(vpath)

    # DevGoal: we can ultimately add an "interactive" trigger that will open the not-yet-made widget. Otherwise, it will use the var_list passed by the user/defaults
    def remove(self, all=False, var_list=None, beam_list=None, keyword_list=None):
        """
        Remove the variables and paths from the wanted list using user specified beam, keyword,
         and variable lists.

        Parameters:
        -----------
        all : boolean, default False
            Remove all variables and paths from the wanted list.

        var_list : list of strings, default None
            A list of variables to request, if not all available variables are wanted.
            A list of available variables can be obtained by entering `var_list=['']` into the function.

        beam_list : list of strings, default None
            A list of beam strings, if only selected beams are wanted (the default value of None will automatically
            include all beams). For ATL09, acceptable values are ['profile_1', 'profile_2', 'profile_3'].
            For all other products, acceptable values are ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r'].

        keyword_list : list of strings, default None
            A list of subdirectory names (keywords), from any heirarchy level within the data structure, to select variables within
            the product that include that keyword in their path.

        Notes
        -----
        See also the `ICESat-2_DAAC_DataAccess2_Subsetting
        <https://github.com/icesat2py/icepyx/blob/main/doc/examples/ICESat-2_DAAC_DataAccess2_Subsetting.ipynb>`_
        example notebook

        Examples
        --------
        >>> reg_a = icepyx.query.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.earthdata_login(user_id,user_email)
        Earthdata Login password:  ········

        To clear the list of wanted variables

        >>> reg_a.order_vars.remove(all=True)

        To remove all variables related to a specific ICESat-2 beam

        >>> reg_a.order_vars.remove(beam_list=['gt1r'])

        To remove specific variables in orbit_info

        >>> reg_a.order_vars.remove(keyword_list=['orbit_info'],var_list=['sc_orient_time'])

        To remove all variables and paths in ancillary_data

        >>> reg_a.order_vars.remove(keyword_list=['ancillary_data'])
        """

        if not hasattr(self, "wanted") or self.wanted == None:
            raise ValueError(
                "You must construct a wanted variable list in order to remove values from it."
            )

        assert not (
            all == False
            and var_list == None
            and beam_list == None
            and keyword_list == None
        ), "You must specify which variables/paths/beams you would like to remove from your wanted list."

        # if not hasattr(self, 'avail'): self.get_avail()
        # vgrp, paths = self.parse_var_list(self.avail)
        # # vgrp, paths = self.parse_var_list(self._cust_options['variables'])
        # allpaths = []
        # [allpaths.extend(np.unique(np.array(paths[p]))) for p in range(len(paths))]
        # allpaths = np.unique(allpaths)

        # self._check_valid_lists(vgrp, allpaths, var_list, beam_list, keyword_list)

        if all == True:
            try:
                self.wanted = None
            except NameError:
                pass

        else:
            # Case only variables (but not keywords or beams) are specified
            if beam_list == None and keyword_list == None:
                for vn in var_list:
                    try:
                        del self.wanted[vn]
                    except KeyError:
                        pass

            # DevGoal: Do we want to enable the user to remove mandatory variables (how it's written now)?
            # Case a beam and/or keyword list is specified (with or without variables)
            else:
                combined_list = self._get_combined_list(beam_list, keyword_list)
                if var_list == None:
                    var_list = self.wanted.keys()

                # nec_varlist = ['sc_orient','atlas_sdp_gps_epoch','data_start_utc','data_end_utc',
                #             'granule_start_utc','granule_end_utc','start_delta_time','end_delta_time']

                for vkey in tuple(var_list):  # self.wanted.keys()):
                    for vpath in tuple(self.wanted[vkey]):
                        vpath_kws = vpath.split("/")

                        try:
                            for bkw in beam_list:
                                if bkw in vpath_kws:
                                    for kw in keyword_list:

                                        if kw in vpath_kws:
                                            self.wanted[vkey].remove(vpath)
                        except TypeError:
                            for kw in combined_list:
                                if kw in vpath_kws and vkey in var_list:
                                    self.wanted[vkey].remove(vpath)

                    try:
                        if self.wanted[vkey] == []:
                            del self.wanted[vkey]
                    except KeyError:
                        pass
