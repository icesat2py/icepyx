from icepyx.quest.dataset_scripts.dataset import DataSet
from icepyx.core.spatial import geodataframe
import requests
import pandas as pd
import os
import numpy as np


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

    # DevNote: it looks like ArgoVis now accepts polygons, not just bounding boxes
    def __init__(self, boundingbox, timeframe):
        super().__init__(boundingbox, timeframe)
        assert self._spatial._ext_type == "bounding_box"
        self.argodata = None
        self._apikey = "92259861231b55d32a9c0e4e3a93f4834fc0b6fa"

    def search_data(self, params=["all"], presRange=None, printURL=False) -> str:
        """
        query argo profiles given the spatio temporal criteria
        and other params specific to the dataset.

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

        # determine which profiles contain all specified params
        # Note: this will be done automatically by Argovis during data download
        if "all" in params:
            prof_ids = []
            for i in selectionProfiles:
                prof_ids.append(i["_id"])
        else:
            prof_ids = self._filter_profiles(selectionProfiles, params)

        self.prof_ids = prof_ids

        msg = "{0} valid profiles have been identified".format(len(prof_ids))
        print(msg)
        return msg

    def _fmt_coordinates(self) -> str:
        """
        Convert spatial extent into string format needed by argovis
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

    # Note: this function may still be useful for users only looking to search for data, but otherwise this filtering is done during download now
    def _filter_profiles(self, profiles, params):
        """
        from a dictionary of all profiles returned by search API request, remove the
        profiles that do not contain ALL measurements specified by user
        returns a list of profile ID's that contain all necessary BGC params
        """
        # todo: filter out BGC profiles
        good_profs = []
        for i in profiles:
            avail_meas = i["data_info"][0]
            check = all(item in avail_meas for item in params)
            if check:
                good_profs.append(i["_id"])
                print(i["_id"])

        return good_profs

    def download_by_profile(self, params, keep_all=True):
        for i in self.prof_ids:
            print("processing profile", i)
            profile_data = self._download_profile(i, params=params, printURL=True)

        self._parse_into_df(profile_data[0])
        self.argodata.reset_index(inplace=True)

    def _download_profile(self, profile_number, params=None, printURL=False):
        # builds URL to be submitted
        baseURL = "https://argovis-api.colorado.edu/argo"
        payload = {
            "id": profile_number,
            "data": params,
        }

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

        # NOTE: may need to use the concat or merge if statement in argobgc
        df = pd.concat([df, profileDf], sort=False)
        self.argodata = df

    def get_dataframe(self, params, keep_existing=True) -> pd.DataFrame:
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
                params.append(p + "_qc")

        self.search_data(params)
        self.download_by_profile(params)

        return self.argodata


# this is just for the purpose of debugging and should be removed later
if __name__ == "__main__":
    # no search results
    # reg_a = Argo([-55, 68, -48, 71], ['2019-02-20', '2019-02-28'])
    # profiles available
    reg_a = Argo([-154, 30, -143, 37], ["2022-04-12", "2022-04-13"])  # "2022-04-26"])

    # Note: this works; will need to see if it carries through
    # Note: run this if you just want valid profile ids (stored as reg_a.prof_ids)
    # it's the first step completed in get_dataframe
    reg_a.search_data(presRange=[], printURL=True)

    reg_a.get_dataframe(params=["pressure", "temperature", "salinity_argoqc"])
    # if it works with list of len 2, try with a longer list...
    reg_a.get_dataframe()

    print(reg_a.profiles[["pres", "temp", "lat", "lon"]].head())
