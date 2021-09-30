"""
Interactive visualization of spatial extent and ICESat-2 elevations
"""
import concurrent.futures
import datetime
import re

import backoff
import dask.array as da
import dask.dataframe as dd
import datashader as ds
import holoviews as hv
import numpy as np
import pandas as pd
import requests
from holoviews.operation.datashader import rasterize
from tqdm import tqdm

import icepyx as ipx
import icepyx.core.is2ref as is2ref
import icepyx.core.granules as granules

hv.extension("bokeh")


def files_in_latest_n_cycles(files, cycles, n=1) -> list:
    """
    Get list of file names from latest n ICESat-2 cycles

    Parameters
    ----------
    files : list
        A list of file names.
    cycles: list
        A list of available ICESat-2 cycles
    n: int, default 1
        Number of latest ICESat-2 cycles to pick

    Returns
    -------
    viz_file_list : list
        A list of file names from latest n ICESat-2 cycles
    """
    if n == 1:
        latest_cycle = max(cycles)
        viz_file_list = [
            f for f in files if int(f.rsplit("_")[-3][4:6]) == latest_cycle
        ]
        return viz_file_list

    elif n > 1:
        if len(cycles) >= n:
            viz_cycle_list = [max(cycles) - i for i in np.arange(n)]
        else:
            viz_cycle_list = cycles
        viz_file_list = [
            f for f in files if int(f.rsplit("_")[-3][4:6]) in viz_cycle_list
        ]
        return viz_file_list

    else:
        raise Exception("Wrong n value")


def gran_paras(filename) -> list:
    """
    Returns a list of granule information for file name string.

    Parameters
    ----------
    filename: String
        ICESat-2 file name

    Returns
    -------
    gran_paras_list : list
        A list of parameters including RGT, cycle, and datetime of ICESat-2 data granule
    """

    trk, cycl, date_str = granules.gran_IDs(
        [{"producer_granule_id": filename}],
        ids=False,
        cycles=True,
        tracks=True,
        dates=True,
    )[:]
    gran_paras_list = [int(cycl[0]), int(trk[0]), date_str[0]]

    return gran_paras_list


def user_check(message):
    """
    Check if user wants to proceed visualization when the API request number exceeds 200

    Parameters
    ----------
    message : string
        Message to indicate users the options
    """
    check = input(message)
    if str(check) == "yes" or str(check) == "no":
        return str(check)
    else:
        user_check("Wrong input, please enter yes or no")


class Visualize:
    """
    Object class to quickly visualize elevation data for select ICESat-2 products
    (ATL06, ATL07, ATL08, ATL10, ATL12, ATL13) based on the query parameters
    defined by the icepyx Query object. Provides interactive maps that show product
    elevation on a satellite basemap.

    Parameters
    ----------
    query_obj : ipx.Query object, default None
        icepy Query class object.
    product : string
        ICESat-2 product ID
    spatial_extent: list or string, default None
        as in the ipx.Query object
    date_range : list of 'YYYY-MM-DD' strings, default None
        as in the ipx.Query object
    cycle : string, default all available orbital cycles, default None
        as in the ipx.Query object
    track : string, default all available reference ground tracks (RGTs), default None
        as in the ipx.Query object

    See Also
    --------
    ipx.Query
    """

    def __init__(
        self,
        query_obj=None,
        product=None,
        spatial_extent=None,
        date_range=None,
        cycles=None,
        tracks=None,
    ):

        if query_obj:
            pass
        else:
            query_obj = ipx.Query(
                product=product,
                spatial_extent=spatial_extent,
                date_range=date_range,
                cycles=cycles,
                tracks=tracks,
            )

        self.product = is2ref._validate_OA_product(query_obj.product)

        if query_obj.extent_type == "bounding_box":
            self.bbox = query_obj._spat_extent

        else:
            mrc_bound = query_obj._spat_extent.minimum_rotated_rectangle
            # generate bounding box
            lonmin = min(mrc_bound.exterior.coords.xy[0])
            lonmax = max(mrc_bound.exterior.coords.xy[0])
            latmin = min(mrc_bound.exterior.coords.xy[1])
            latmax = max(mrc_bound.exterior.coords.xy[1])

            self.bbox = [lonmin, latmin, lonmax, latmax]

        self.date_range = (
            [query_obj._start.strftime("%Y-%m-%d"), query_obj._end.strftime("%Y-%m-%d")]
            if hasattr(query_obj, "_start")
            else None
        )
        self.cycles = query_obj._cycles if hasattr(query_obj, "_cycles") else None
        self.tracks = query_obj._tracks if hasattr(query_obj, "_tracks") else None

    def grid_bbox(self, binsize=5) -> list:
        """
        Split bounding box into 5 x 5 grids when latitude/longitude range
        exceeds the default OpenAltimetry 5*5 degree spatial limits

        Returns
        -------
        bbox_list : list
            A list of bounding boxes with a maximum size of 5*5 degree
        """
        lonmin, latmin, lonmax, latmax = self.bbox
        split_flag = ((lonmax - lonmin) > 5) or ((latmax - latmin) > 5)

        if split_flag:
            # split bounding box into a list of 5*5 bbox
            lonx = np.arange(lonmin, lonmax + binsize, binsize)
            laty = np.arange(latmin, latmax + binsize, binsize)
            lonxv, latyv = np.meshgrid(lonx, laty)

            ydim, xdim = lonxv.shape

            bbox_list = []
            for i in np.arange(0, ydim - 1):
                for j in np.arange(0, xdim - 1):
                    # iterate grid for bounding box
                    bbox_ij = [
                        lonxv[i, j],
                        latyv[i, j],
                        lonxv[i + 1, j + 1],
                        latyv[i + 1, j + 1],
                    ]

                    if bbox_ij[2] > lonmax:
                        bbox_ij[2] = lonmax

                    if bbox_ij[3] > latmax:
                        bbox_ij[3] = latmax

                    bbox_list.append(bbox_ij)

            return bbox_list

        else:
            return [self.bbox]

    def query_icesat2_filelist(self) -> tuple:
        """
        Query list of ICESat-2 files for each bounding box

        Returns
        -------
        filelist_tuple : tuple
            A tuple of non-empty lists of bounding boxes and corresponding ICESat-2 file lists
        """
        # a list of 5*5 bounding boxes
        bbox_list = self.grid_bbox()

        is2_bbox_list = []
        is2_file_list = []

        for bbox_i in bbox_list:

            try:
                region = ipx.Query(
                    self.product,
                    bbox_i,
                    self.date_range,
                    cycles=self.cycles,
                    tracks=self.tracks,
                )
                icesat2_files = region.avail_granules(ids=True)[0]
            except (AttributeError, AssertionError):
                continue

            if not icesat2_files:
                continue
            else:
                all_cycles = list(set(region.avail_granules(cycles=True)[0]))
                icesat2_files_latest_cycle = files_in_latest_n_cycles(
                    icesat2_files, [int(c) for c in all_cycles]
                )
                is2_bbox_list.append(bbox_i)
                is2_file_list.append(icesat2_files_latest_cycle)

        is2_file_tuple = zip(is2_bbox_list, is2_file_list)

        return is2_file_tuple

    def generate_OA_parameters(self) -> list:
        """
        Get metadata from file lists in each 5*5 bounding box.

        Returns
        -------
        paras_list : list
            A list of parameters for OpenAltimetry API query, including the
            reference ground track (RGT), cycle number, datetime, bounding box,
            and product name.
        """
        # list of parameters for API query
        paras_list = []

        # tuple of non-empty bbox and ICESat-2 datafiles
        filelist_tuple = self.query_icesat2_filelist()

        for bbox_i, filelist in filelist_tuple:
            for fname in filelist:
                rgt, cycle, f_date = gran_paras(fname)
                paras = [rgt, f_date, cycle, bbox_i, self.product]
                paras_list.append(paras)

        return paras_list

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ),
        max_tries=5,
    )
    def make_request(self, base_url, payload):
        """
        Make HTTP request

        Parameters
        ----------
        base_url : string
            OpenAltimetry URL

        See Also
        --------
        request_OA_data
        """
        return requests.get(base_url, params=payload)

    def request_OA_data(self, paras) -> da.array:
        """
        Request data from OpenAltimetry based on API:
        https://openaltimetry.org/data/swagger-ui/#/

        Parameters
        ----------
        paras : list
            A single parameter list for an OpenAltimetry API data request.

        Returns
        -------
        OA_darr : da.array
            A dask array containing the ICESat-2 elevation data.
        """

        base_url = "https://openaltimetry.org/data/api/icesat2/level3a"
        trackId, Date, cycle, bbox, product = paras

        # Generate API
        payload = {
            "product": product.lower(),
            "endDate": Date,
            "minx": str(bbox[0]),
            "miny": str(bbox[1]),
            "maxx": str(bbox[2]),
            "maxy": str(bbox[3]),
            "trackId": trackId,
            "outputFormat": "json",
        }  # default return all six beams

        # request OpenAltimetry
        r = self.make_request(base_url, payload)

        # get elevation data
        elevation_data = r.json()

        df = pd.json_normalize(data=elevation_data, record_path=["data"])

        # get data we need (with the correct date)
        try:

            df_series = df.query(expr="date == @Date").iloc[0]
            beam_data = df_series.beams

        except (NameError, KeyError, IndexError) as error:
            beam_data = None

        if not beam_data:
            return

        data_name = "lat_lon_elev_canopy" if product == "ATL08" else "lat_lon_elev"

        sample_rate = 50 if product == "ATL06" else 20

        # iterate six beams
        beam_elev = [
            beam_data[i][data_name][::sample_rate]
            for i in range(6)
            if beam_data[i][data_name]
        ]

        if not beam_elev:
            return

        # elevation for all available beams
        OA_array = np.vstack(beam_elev)

        if OA_array.shape[0] > 0:
            OA_array = np.c_[
                OA_array,
                np.full(np.size(OA_array, 0), trackId),
                np.full(np.size(OA_array, 0), cycle),
            ]
            OA_darr = da.from_array(OA_array, chunks=1000)

            return OA_darr

    def parallel_request_OA(self) -> da.array:
        """
        Requests elevation data from OpenAltimetry API in parallel.
        Currently supports OA_Products ['ATL06','ATL07','ATL08','ATL10','ATL12','ATL13']

        For ATL03 Photon Data, OA only supports single date request
        according to: https://openaltimetry.org/data/swagger-ui/#/Public/getATL08DataByDate,
        with geospatial limitation of 1 degree lat/lon. Visualization of ATL03 data
        is not implemented within this module at this time.

        Returns
        -------
        OA_data_da : dask.Array
            A dask array containing the ICESat-2 data.
        """
        print("Generating urls")

        # generate parameter lists for OA requesting
        OA_para_list = self.generate_OA_parameters()

        assert OA_para_list, "Your search returned no results; try different search parameters"

        url_number = len(OA_para_list)

        if url_number > 200:
            answer = user_check(
                "Too many API requests, this may take a long time, do you still want to continue: "
                "please enter yes/no\n"
            )

            if answer == "yes":
                pass
            else:
                return

        print("Sending request to OpenAltimetry, please wait...")

        # Parallel processing
        requested_OA_data = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(OA_para_list)
        ) as executor:
            parallel_OA_data = {
                executor.submit(self.request_OA_data, para): para
                for para in OA_para_list
            }

            for future in tqdm(
                iterable=concurrent.futures.as_completed(parallel_OA_data),
                total=len(parallel_OA_data),
            ):
                r = future.result()
                if r is not None:
                    requested_OA_data.append(r)

        if not requested_OA_data:
            return
        else:
            OA_data_da = da.concatenate(requested_OA_data, axis=0)
            return OA_data_da

    def viz_elevation(self) -> (hv.DynamicMap, hv.Layout):
        """
        Visualize elevation requested from OpenAltimetry API using datashader based on cycles
        https://holoviz.org/tutorial/Large_Data.html

        Returns
        -------
        map_cycle, map_rgt + lineplot_rgt : Holoviews objects
            Holoviews data visualization elements
        """

        OA_da = self.parallel_request_OA()

        if OA_da is None:
            print("No data")
            return (None,) * 2

        else:

            cols = (
                ["lat", "lon", "elevation", "canopy", "rgt", "cycle"]
                if self.product == "ATL08"
                else ["lat", "lon", "elevation", "rgt", "cycle"]
            )
            ddf = dd.io.from_dask_array(OA_da, columns=cols).astype(
                {
                    "lat": "float",
                    "lon": "float",
                    "elevation": "float",
                    "rgt": "int",
                    "cycle": "int",
                }
            )

            print("Plot elevation, please wait...")

            x, y = ds.utils.lnglat_to_meters(ddf.lon, ddf.lat)
            ddf_new = ddf.assign(x=x, y=y).persist()
            dset = hv.Dataset(ddf_new)

            raster_cycle = dset.to(
                hv.Points,
                ["x", "y"],
                ["elevation"],
                groupby=["cycle"],
                dynamic=True,
            )
            raster_rgt = dset.to(
                hv.Points, ["x", "y"], ["elevation"], groupby=["rgt"], dynamic=True
            )
            curve_rgt = dset.to(
                hv.Scatter, ["lat"], ["elevation"], groupby=["rgt"], dynamic=True
            )

            tiles = hv.element.tiles.EsriImagery().opts(
                xaxis=None, yaxis=None, width=450, height=450
            )
            map_cycle = tiles * rasterize(
                raster_cycle, aggregator=ds.mean("elevation")
            ).opts(colorbar=True, tools=["hover"])
            map_rgt = tiles * rasterize(
                raster_rgt, aggregator=ds.mean("elevation")
            ).opts(colorbar=True, tools=["hover"])
            lineplot_rgt = rasterize(curve_rgt, aggregator=ds.mean("elevation")).opts(
                width=450, height=450, cmap=["blue"]
            )

            return map_cycle, map_rgt + lineplot_rgt
