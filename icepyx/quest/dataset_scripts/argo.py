import os.path

import numpy as np
import pandas as pd
import requests

from icepyx.core.spatial import geodataframe
from icepyx.quest.dataset_scripts.dataset import DataSet


class Argo(DataSet):
    """
    Initialises an Argo Dataset object via a Quest object.
    Used to query physical and BGC Argo profiles.

    Parameters
    ---------
    aoi :
        area of interest supplied via the spatial parameter of the QUEST object
    toi :
        time period of interest supplied via the temporal parameter of the QUEST object
    params : list of str, default ["temperature"]
        A list of strings, where each string is a requested parameter.
        Only metadata for profiles with the requested parameters are returned.
        To search for all parameters, use `params=["all"]`;
        be careful using all for floats with BGC data, as this may be result in a large download.
    presRange : str, default None
        The pressure range (which correlates with depth) to search for data within.
        Input as a "shallow-limit,deep-limit" string.

    See Also
    --------
    DataSet
    """

    # Note: it looks like ArgoVis now accepts polygons, not just bounding boxes
    def __init__(self, aoi, toi, params=["temperature"], presRange=None):
        self._params = self._validate_parameters(params)
        self._presRange = presRange
        self._spatial = aoi
        self._temporal = toi
        # todo: verify that this will only work with a bounding box (I think our code can accept arbitrary polygons)
        assert self._spatial._ext_type == "bounding_box"
        self.argodata = None
        self._apikey = "92259861231b55d32a9c0e4e3a93f4834fc0b6fa"

    def __str__(self):
        prange = "All" if self.presRange is None else str(self.presRange)

        if self.argodata is None:
            df = "No data yet"
        else:
            df = "\n" + str(self.argodata.head())
        s = (
            "---Argo---\n"
            "Parameters: {0}\n"
            "Pressure range: {1}\n"
            "Dataframe head: {2}".format(self.params, prange, df)
        )

        return s

    # ----------------------------------------------------------------------
    # Properties

    @property
    def params(self) -> list:
        """
        User's list of Argo parameters to search (query) and download.

        The user may modify this list directly.
        """

        return self._params

    @params.setter
    def params(self, value):
        """
        Validate the input list of parameters.
        """

        self._params = list(set(self._validate_parameters(value)))

    @property
    def presRange(self) -> str:
        """
        User's pressure range to search (query) and download.

        The user may modify this string directly.
        """

        return self._presRange

    @presRange.setter
    def presRange(self, value):
        """
        Update the presRange based on the user input
        """

        self._presRange = value

    # ----------------------------------------------------------------------
    # Formatting API Inputs

    def _fmt_coordinates(self) -> str:
        """
        Convert spatial extent into string format needed by argovis API
        i.e. list of polygon coords [[[lat1,lon1],[lat2,lon2],...]]
        """

        gdf = geodataframe(self._spatial._ext_type, self._spatial._spatial_ext)
        coordinates_array = np.asarray(gdf.geometry[0].exterior.coords)
        x = ""
        for i in coordinates_array:
            coord = "[{0},{1}]".format(i[0], i[1])
            if x == "":
                x = coord
            else:
                x += "," + coord

        x = "[" + x + "]"
        return x

    # ----------------------------------------------------------------------
    # Validation

    def _valid_params(self) -> list:
        """
        A list of valid Argo measurement parameters (including BGC).

        To get a list of valid parameters, comment out the validation line in `search_data` herein,
        submit a search with an invalid parameter, and get the list from the response.
        """

        valid_params = [
            # all argo
            "pressure",
            "pressure_argoqc",
            "salinity",
            "salinity_argoqc",
            "salinity_sfile",
            "salinity_sfile_argoqc",
            "temperature",
            "temperature_argoqc",
            "temperature_sfile",
            "temperature_sfile_argoqc",
            # BGC params
            "bbp470",
            "bbp470_argoqc",
            "bbp532",
            "bbp532_argoqc",
            "bbp700",
            "bbp700_argoqc",
            "bbp700_2",
            "bbp700_2_argoqc",
            "bisulfide",
            "bisulfide_argoqc",
            "cdom",
            "cdom_argoqc",
            "chla",
            "chla_argoqc",
            "cndc",
            "cndc_argoqc",
            "cndx",
            "cndx_argoqc",
            "cp660",
            "cp660_argoqc",
            "down_irradiance380",
            "down_irradiance380_argoqc",
            "down_irradiance412",
            "down_irradiance412_argoqc",
            "down_irradiance442",
            "down_irradiance442_argoqc",
            "down_irradiance443",
            "down_irradiance443_argoqc",
            "down_irradiance490",
            "down_irradiance490_argoqc",
            "down_irradiance555",
            "down_irradiance555_argoqc",
            "down_irradiance670",
            "down_irradiance670_argoqc",
            "downwelling_par",
            "downwelling_par_argoqc",
            "doxy",
            "doxy_argoqc",
            "doxy2",
            "doxy2_argoqc",
            "doxy3",
            "doxy3_argoqc",
            "molar_doxy",
            "molar_doxy_argoqc",
            "nitrate",
            "nitrate_argoqc",
            "ph_in_situ_total",
            "ph_in_situ_total_argoqc",
            "turbidity",
            "turbidity_argoqc",
            "up_radiance412",
            "up_radiance412_argoqc",
            "up_radiance443",
            "up_radiance443_argoqc",
            "up_radiance490",
            "up_radiance490_argoqc",
            "up_radiance555",
            "up_radiance555_argoqc",
            # all params
            "all",
        ]
        return valid_params

    def _validate_parameters(self, params) -> list:
        """
        Checks that the list of user requested parameters are valid.

        Returns
        -------
        The list of valid parameters
        """

        if "all" in params:
            params = ["all"]
        else:
            valid_params = self._valid_params()
            # checks that params are valid
            for i in params:
                assert i in valid_params, (
                    "Parameter '{0}' is not valid. Valid parameters are {1}".format(
                        i, valid_params
                    )
                )

        return list(set(params))

    # ----------------------------------------------------------------------
    # Querying and Getting Data

    def search_data(self, params=None, presRange=None, printURL=False) -> str:
        """
        Query for available argo profiles given the spatio temporal criteria
        and other params specific to the dataset.
        Searches will automatically use the parameter and pressure range inputs
        supplied when the `quest.argo` object was created unless replacement arguments
        are added here.

        Parameters
        ---------
        params : list of str, default None
            A list of strings, where each string is a requested parameter.
            This kwarg is used to replace the existing list in `self.params`.
            Do not submit this kwarg if you would like to use the existing `self.params` list.
            Only metadata for profiles with the requested parameters are returned.
            To search for all parameters, use `params=["all"]`;
            be careful using all for floats with BGC data, as this may be result in a large download.
        presRange : str, default None
            The pressure range (which correllates with depth) to search for data within.
            This kwarg is used to replace the existing pressure range in `self.presRange`.
            Do not submit this kwarg if you would like to use the existing `self.presRange` values.
            Input as a "shallow-limit,deep-limit" string.
        printURL : boolean, default False
            Print the URL of the data request. Useful for debugging and when no data is returned.

        Returns
        ------
        str : message on the success status of the search
        """

        # if search is called with replaced parameters or presRange
        if params is not None:
            self.params = params

        if presRange is not None:
            self.presRange = presRange

        # builds URL to be submitted
        baseURL = "https://argovis-api.colorado.edu/argo"
        payload = {
            "startDate": self._temporal._start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endDate": self._temporal._end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "polygon": [self._fmt_coordinates()],
            "data": self.params,
        }

        if self.presRange is not None:
            payload["presRange"] = self.presRange

        # submit request
        resp = requests.get(
            baseURL, headers={"x-argokey": self._apikey}, params=payload
        )

        if printURL:
            print(resp.url)

        selectionProfiles = resp.json()

        # Consider any status other than 2xx an error
        if resp.status_code // 100 != 2:
            # check for the existence of profiles from query
            if selectionProfiles == []:
                msg = (
                    "Warning: Query returned no profiles\n"
                    "Please try different search parameters"
                )
                print(msg)
                return msg

            else:
                msg = "Error: Unexpected response {}".format(resp)
                print(msg)
                return msg

        # record the profile ids for the profiles that contain the requested parameters
        prof_ids = []
        for i in selectionProfiles:
            prof_ids.append(i["_id"])
        # should we be doing a set/duplicates check here??
        self.prof_ids = prof_ids

        msg = "{0} valid profiles have been identified".format(len(prof_ids))
        print(msg)
        return msg

    def _download_profile(
        self,
        profile_number,
        printURL=False,
    ) -> dict:
        """
        Download available argo data for a particular profile_ID.

        Parameters
        ---------
        profile_number: str
            String containing the argo profile ID of the data being downloaded.
        printURL: boolean, default False
            Print the URL of the data request. Useful for debugging and when no data is returned.

        Returns
        ------
        dict : json formatted dictionary of the profile data
        """

        # builds URL to be submitted
        baseURL = "https://argovis-api.colorado.edu/argo"
        payload = {
            "id": profile_number,
            "data": self.params,
        }

        if self.presRange:
            payload["presRange"] = self.presRange

        # submit request
        resp = requests.get(
            baseURL, headers={"x-argokey": self._apikey}, params=payload
        )

        if printURL:
            print(resp.url)

        # Consider any status other than 2xx an error
        if resp.status_code // 100 != 2:
            return "Error: Unexpected response {}".format(resp)
        profile = resp.json()
        return profile

    def _parse_into_df(self, profile_data) -> pd.DataFrame:
        """
        Parses downloaded data from a single profile into dataframe.
        Appends data to any existing profile data stored in the `argodata` property.

        Parameters
        ----------
        profile_data: dict
            The downloaded profile data.
            The data is contained in the requests response and converted into a json formatted dictionary
            by `_download_profile` before being passed into this function.

        Returns
        -------
        pd.DataFrame : DataFrame of profile data
        """

        profileDf = pd.DataFrame(
            np.transpose(profile_data["data"]), columns=profile_data["data_info"][0]
        )

        # this block tries to catch changes to the ArgoVis API that will break the dataframe creation
        try:
            profileDf["profile_id"] = profile_data["_id"]
            # there's also a geolocation field that provides the geospatial info as shapely points
            profileDf["lat"] = profile_data["geolocation"]["coordinates"][1]
            profileDf["lon"] = profile_data["geolocation"]["coordinates"][0]
            profileDf["date"] = profile_data["timestamp"]
        except KeyError as err:
            msg = "We cannot automatically parse your profile into a dataframe due to {0}".format(
                err
            )
            print(msg)
            return msg

        profileDf.replace("None", np.nan, inplace=True, regex=True)

        return profileDf

    def download(self, params=None, presRange=None, keep_existing=True) -> pd.DataFrame:
        """
        Downloads the requested data for a list of profile IDs (stored under .prof_ids) and returns it in a DataFrame.

        Data is also stored in self.argodata.
        Note that if new inputs (`params` or `presRange`) are supplied and `keep_existing=True`,
        the existing data will not be limited to the new input parameters.

        Parameters
        ----------
        params : list of str, default None
            A list of strings, where each string is a requested parameter.
            This kwarg is used to replace the existing list in `self.params`.
            Do not submit this kwarg if you would like to use the existing `self.params` list.
            Only metadata for profiles with the requested parameters are returned.
            To search for all parameters, use `params=["all"]`.
            For a list of available parameters, see: `reg._valid_params`
        presRange : str, default None
            The pressure range (which correllates with depth) to search for data within.
            This kwarg is used to replace the existing pressure range in `self.presRange`.
            Do not submit this kwarg if you would like to use the existing `self.presRange` values.
            Input as a "shallow-limit,deep-limit" string.
        keep_existing : boolean, default True
            Provides the option to clear any existing downloaded data before downloading more.

        Returns
        -------
        pd.DataFrame : DataFrame of requested data
        """

        # TODO: do some basic testing of this block and how the dataframe merging actually behaves
        if keep_existing is False:
            print(
                "Your previously stored data in reg.argodata",
                "will be deleted before new data is downloaded.",
            )
            self.argodata = None
        elif keep_existing is True and hasattr(self, "argodata"):
            print(
                "The data requested by running this line of code\n",
                "will be added to previously downloaded data.",
            )

        # if download is called with replaced parameters or presRange
        if params is not None:
            self.params = params

        if presRange is not None:
            self.presRange = presRange

        # Add qc data for each of the parameters requested
        if self.params == ["all"]:
            pass
        else:
            for p in self.params:
                if p.endswith("_argoqc") or (p + "_argoqc" in self.params):
                    pass
                else:
                    self.params.append(p + "_argoqc")

        # intentionally resubmit search to reset prof_ids, in case the user requested different parameters
        self.search_data()

        # create a dataframe for each profile and merge it with the rest of the profiles from this set of parameters being downloaded
        merged_df = pd.DataFrame(columns=["profile_id"])
        for i in self.prof_ids:
            print("processing profile", i)
            try:
                profile_data = self._download_profile(i)
                profile_df = self._parse_into_df(profile_data[0])
                merged_df = pd.concat([merged_df, profile_df], sort=False)
            except Exception:
                print("\tError processing profile {0}. Skipping.".format(i))

        # now that we have a df from this round of downloads, we can add it to any existing dataframe
        # note that if a given column has previously been added, update needs to be used to replace nans (merge will not replace the nan values)
        if self.argodata is not None:
            self.argodata = self.argodata.merge(merged_df, how="outer")
        else:
            self.argodata = merged_df

        self.argodata.reset_index(inplace=True, drop=True)

        return self.argodata

    def save(self, filepath):
        """
        Saves the argo dataframe to a csv at the specified location

        Parameters
        ----------
        filepath : str
            String containing complete filepath and name of file
            Any extension will be removed and replaced with csv.
            Also appends '_argo.csv' to filename
            e.g. /path/to/file/my_data(_argo.csv)
        """

        # create the directory if it doesn't exist
        path, file = os.path.split(filepath)
        if not os.path.exists(path):
            os.mkdir(path)

        # remove any file extension
        base, ext = os.path.splitext(filepath)

        self.argodata.to_csv(base + "_argo.csv")
