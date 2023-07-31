import numpy as np
import pandas as pd
import requests

from icepyx.core.spatial import geodataframe
from icepyx.quest.dataset_scripts.dataset import DataSet


class Argo(DataSet):
    """
    Initialises an Argo Dataset object
    Used to query physical Argo profiles
    -> biogeochemical Argo (BGC) not included

    Examples
    --------
    # example with profiles available
    >>> reg_a = Argo([-154, 30,-143, 37], ['2022-04-12', '2022-04-26'])
    >>> reg_a.search_data()
    >>> print(reg_a.profiles[['pres', 'temp', 'lat', 'lon']].head())
        pres    temp     lat      lon
    0   3.9  18.608  33.401 -153.913
    1   5.7  18.598  33.401 -153.913
    2   7.7  18.588  33.401 -153.913
    3   9.7  18.462  33.401 -153.913
    4  11.7  18.378  33.401 -153.913

    # example with no profiles
    >>> reg_a = Argo([-55, 68, -48, 71], ['2019-02-20', '2019-02-28'])
    >>> reg_a.search_data()
    Warning: Query returned no profiles
    Please try different search parameters

    See Also
    --------
    DataSet
    GenQuery
    """

    # Note: it looks like ArgoVis now accepts polygons, not just bounding boxes
    def __init__(self, boundingbox, timeframe):
        super().__init__(boundingbox, timeframe)
        assert self._spatial._ext_type == "bounding_box"
        self.argodata = None
        self._apikey = "92259861231b55d32a9c0e4e3a93f4834fc0b6fa"

    def search_data(
        self, params=["temperature"], presRange=None, printURL=False
    ) -> str:
        """
        Query for available argo profiles given the spatio temporal criteria
        and other params specific to the dataset.

        Parameters
        ---------
        params: list of str, default ["temperature", "pressure]
            A list of strings, where each string is a requested parameter.
            Only metadata for profiles with the requested parameters are returned.
            To search for all parameters, use `params=["all"]`.
            For a list of available parameters, see:
        presRange: str, default None
            The pressure range (which correllates with depth) to search for data within.
            Input as a "shallow-limit,deep-limit" string. Note the lack of space.
        printURL: boolean, default False
            Print the URL of the data request. Useful for debugging and when no data is returned.

        Returns
        ------
        str: message on the success status of the search
        """

        params = self._validate_parameters(params)
        print(params)

        # builds URL to be submitted
        baseURL = "https://argovis-api.colorado.edu/argo"
        payload = {
            "startDate": self._temporal._start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endDate": self._temporal._end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "polygon": [self._fmt_coordinates()],
            "data": params,
        }
        if presRange:
            payload["presRange"] = presRange

        # submit request
        resp = requests.get(
            baseURL, headers={"x-argokey": self._apikey}, params=payload
        )

        if printURL:
            print(resp.url)

        selectionProfiles = resp.json()

        # Consider any status other than 2xx an error
        if not resp.status_code // 100 == 2:
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
        self.prof_ids = prof_ids

        msg = "{0} valid profiles have been identified".format(len(prof_ids))
        print(msg)
        return msg

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
                assert (
                    i in valid_params
                ), "Parameter '{0}' is not valid. Valid parameters are {1}".format(
                    i, valid_params
                )

        return params

    def _download_profile(
        self,
        profile_number,
        params=None,
        presRange=None,
        printURL=False,
    ) -> dict:
        """
        Download available argo data for a particular profile_ID.

        Parameters
        ---------
        profile_number: str
            String containing the argo profile ID of the data being downloaded.
        params: list of str, default ["temperature", "pressure]
            A list of strings, where each string is a requested parameter.
            Only data for the requested parameters are returned.
            To download all parameters, use `params=["all"]`.
            For a list of available parameters, see:
        presRange: str, default None
            The pressure range (which correllates with depth) to download data within.
            Input as a "shallow-limit,deep-limit" string. Note the lack of space.
        printURL: boolean, default False
            Print the URL of the data request. Useful for debugging and when no data is returned.

        Returns
        ------
        dict: json formatted dictionary of the profile data
        """

        # builds URL to be submitted
        baseURL = "https://argovis-api.colorado.edu/argo"
        payload = {
            "id": profile_number,
            "data": params,
        }

        if presRange:
            payload["presRange"] = presRange

        # submit request
        resp = requests.get(
            baseURL, headers={"x-argokey": self._apikey}, params=payload
        )

        if printURL:
            print(resp.url)

        # Consider any status other than 2xx an error
        if not resp.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(resp)
        profile = resp.json()
        return profile

    # todo: add a try/except to make sure the json files are valid i.e. contains all data we're expecting (no params are missing)
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
        pandas DataFrame of the profile data
        """

        profileDf = pd.DataFrame(
            np.transpose(profile_data["data"]), columns=profile_data["data_info"][0]
        )
        profileDf["profile_id"] = profile_data["_id"]
        # there's also a geolocation field that provides the geospatial info as shapely points
        profileDf["lat"] = profile_data["geolocation"]["coordinates"][1]
        profileDf["lon"] = profile_data["geolocation"]["coordinates"][0]
        profileDf["date"] = profile_data["timestamp"]

        profileDf.replace("None", np.nan, inplace=True, regex=True)

        return profileDf

    def get_dataframe(self, params, presRange=None, keep_existing=True) -> pd.DataFrame:
        """
        Downloads the requested data for a list of profile IDs (stored under .prof_ids) and returns it in a DataFrame.

        Data is also stored in self.argodata.

        Parameters
        ----------
        params: list of str, default ["temperature", "pressure]
            A list of strings, where each string is a requested parameter.
            Only metadata for profiles with the requested parameters are returned.
            To search for all parameters, use `params=["all"]`.
            For a list of available parameters, see: `reg._valid_params`
        presRange: str, default None
            The pressure range (which correllates with depth) to search for data within.
            Input as a "shallow-limit,deep-limit" string. Note the lack of space.
        keep_existing: Boolean, default True
            Provides the option to clear any existing downloaded data before downloading more.

        Returns
        -------
        pd.DataFrame: DataFrame of requested data
        """

        # TODO: do some basic testing of this block and how the dataframe merging actually behaves
        if keep_existing == False:
            print(
                "Your previously stored data in reg.argodata",
                "will be deleted before new data is downloaded.",
            )
            self.argodata = None
        elif keep_existing == True and hasattr(self, "argodata"):
            print(
                "The data requested by running this line of code\n",
                "will be added to previously downloaded data.",
            )

        # Add qc data for each of the parameters requested
        if params == ["all"]:
            pass
        else:
            for p in params:
                if p.endswith("_argoqc") or (p + "_argoqc" in params):
                    pass
                else:
                    params.append(p + "_argoqc")

        # intentionally resubmit search to reset prof_ids, in case the user requested different parameters
        self.search_data(params, presRange=presRange)

        # create a dataframe for each profile and merge it with the rest of the profiles from this set of parameters being downloaded
        merged_df = pd.DataFrame(columns=["profile_id"])
        for i in self.prof_ids:
            print("processing profile", i)
            profile_data = self._download_profile(
                i, params=params, presRange=presRange, printURL=True
            )
            profile_df = self._parse_into_df(profile_data[0])
            merged_df = pd.concat([merged_df, profile_df], sort=False)

        # now that we have a df from this round of downloads, we can add it to any existing dataframe
        # note that if a given column has previously been added, update needs to be used to replace nans (merge will not replace the nan values)
        if not self.argodata is None:
            self.argodata = self.argodata.merge(merged_df, how="outer")
        else:
            self.argodata = merged_df

        self.argodata.reset_index(inplace=True, drop=True)

        return self.argodata


"""
        # pandas isn't excelling because of trying to concat or merge for each profile added.
        # if the columns have already been concatted for another profile, we'd need to update to replace nans, not merge
        # if the columns haven't been concatted, we'd need to merge.
        # options: check for columns and have merge and update and concat pathways OR constructe a df for each request and just merge them after the fact 
        # (which might make more sense conceptually and be easier to debug)
        if profile_data["_id"] in df["profile_id"].unique():
            print("merging")
            df = df.merge(profileDf, how="outer")
        else:
            print("concatting")
            df = pd.concat([df, profileDf], sort=False)
"""


# this is just for the purpose of debugging and should be removed later
if __name__ == "__main__":
    # no search results
    # reg_a = Argo([-55, 68, -48, 71], ["2019-02-20", "2019-02-28"])
    # profiles available
    # reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2022-04-13"])  # "2022-04-26"])

    # bgc profiles available
    reg_a = Argo([-150, 30, -120, 60], ["2022-06-07", "2022-06-14"])

    param_list = ["down_irradiance412"]
    bad_param = ["up_irradiance412"]
    # param_list = ["doxy"]

    # reg_a.search_data(params=bad_param, printURL=True)

    reg_a.get_dataframe(params=param_list)

    reg_a.get_dataframe(params=["doxy"], keep_existing=True)  # , presRange="0.2,100"
    # )

    print(reg_a)
