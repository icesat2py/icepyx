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
        self, params=["temperature", "pressure"], presRange=None, printURL=False
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

        # Consider any status other than 2xx an error
        if not resp.status_code // 100 == 2:
            msg = "Error: Unexpected response {}".format(resp)
            print(msg)
            return msg

        selectionProfiles = resp.json()

        # check for the existence of profiles from query
        if selectionProfiles == []:
            msg = (
                "Warning: Query returned no profiles\n"
                "Please try different search parameters"
            )
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

    # TODO: contact argovis for a list of valid params (swagger api docs are a blank page)
    def _valid_params(self) -> list:
        """
        A list of valid Argo measurement parameters.
        """
        valid_params = [
            "doxy",
            "doxy_argoqc",
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

    def download_by_profile(self, params, presRange=None) -> None:
        """
        For a list of profiles IDs (stored under .prof_ids), download the data requested for each one.

        Parameters
        ----------
        params: list of str, default ["temperature", "pressure]
            A list of strings, where each string is a requested parameter.
            Only metadata for profiles with the requested parameters are returned.
            To search for all parameters, use `params=["all"]`.
            For a list of available parameters, see:
        presRange: str, default None
            The pressure range (which correllates with depth) to search for data within.
            Input as a "shallow-limit,deep-limit" string. Note the lack of space.

        Returns
        -------
        None; outputs are stored in the .argodata property.
        """
        # TODO: Need additional checks here?
        if not hasattr(self, "prof_ids"):
            self.search_data(params, presRange=presRange)

        for i in self.prof_ids:
            print("processing profile", i)
            profile_data = self._download_profile(
                i, params=params, presRange=presRange, printURL=True
            )
            self._parse_into_df(profile_data[0])
            self.argodata.reset_index(inplace=True, drop=True)

    def _download_profile(
        self, profile_number, params=None, presRange=None, printURL=False
    ):
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
    def _parse_into_df(self, profile_data) -> None:
        """
        Stores downloaded data from a single profile into dataframe.
        Appends data to any existing profile data stored in self.argodata.

        Returns
        -------
        None
        """

        if not self.argodata is None:
            df = self.argodata
        else:
            df = pd.DataFrame()

        # parse the profile data into a dataframe
        profileDf = pd.DataFrame(
            np.transpose(profile_data["data"]), columns=profile_data["data_info"][0]
        )
        profileDf["profile_id"] = profile_data["_id"]
        # there's also a geolocation field that provides the geospatial info as shapely points
        profileDf["lat"] = profile_data["geolocation"]["coordinates"][1]
        profileDf["lon"] = profile_data["geolocation"]["coordinates"][0]
        profileDf["date"] = profile_data["timestamp"]

        df = pd.concat([df, profileDf], sort=False)
        self.argodata = df

    # next steps: reconcile download by profile and get_dataframe. They need to have clearer division of labor
    def get_dataframe(self, params, presRange=None, keep_existing=True) -> pd.DataFrame:
        """
        Downloads the requested data and returns it in a DataFrame.

        Data is also stored in self.argodata.

        Parameters
        ----------
        params: list of str
            A list of all the measurement parameters requested by the user.

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
                if p.endswith("_argoqc"):
                    pass
                else:
                    params.append(p + "_argoqc")

        self.search_data(params, presRange=presRange)
        self.download_by_profile(params, presRange=presRange)

        return self.argodata


# this is just for the purpose of debugging and should be removed later
if __name__ == "__main__":
    # no search results
    # reg_a = Argo([-55, 68, -48, 71], ['2019-02-20', '2019-02-28'])
    # profiles available
    reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2023-04-13"])  # "2022-04-26"])

    reg_a.search_data(printURL=True)

    reg_a.search_data(params=["doxy"])

    reg_a.get_dataframe(
        params=["pressure", "temperature", "salinity_argoqc"], presRange="0.2,100"
    )
    # if it works with list of len 2, try with a longer list...
