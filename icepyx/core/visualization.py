"""
Interactive visualization of spatial extent and ICESat-2 elevations
"""
import backoff
import concurrent.futures
import dask.array as da
import dask.dataframe as dd
import datashader as ds
import holoviews as hv
from holoviews.operation.datashader import rasterize
import intake.source.utils
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

import icepyx as ipx

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


def user_check(message):
    """
    Check if user wants to proceed visualization when the API request number exceeds 200

    Parameters
    ----------
    message : string
        Message to indicate users the options
    """
    check = input(message)
    if str(check) == 'yes' or str(check) == 'no':
        return str(check)
    else:
        user_check('Wrong input, please enter yes or no')


class Visualize:
    def __init__(self, product, bbox, date_range=None, cycles=None, tracks=None):
        self.product = product
        self.bbox = bbox
        self.date_range = date_range
        self.cycles = cycles
        self.tracks = tracks

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
        Query list of ICESat-2 files based on splitted bbox

        Returns
        -------
        filelist_tuple : tuple
            A tuple of non-empty list of bounding boxes and corresponding ICESat-2 file lists
        """
        # a list of 5*5 bounding boxes
        bbox_list = self.grid_bbox()

        is2_bbox_list = []
        is2_file_list = []

        for bbox_i in bbox_list:

            region = ipx.Query(
                self.product,
                bbox_i,
                self.date_range,
                cycles=self.cycles,
                tracks=self.tracks,
            )
            icesat2_files = region.avail_granules(ids=True)[0]
            all_cycles = list(set(region.avail_granules(cycles=True)[0]))

            if not icesat2_files:
                continue
            else:
                icesat2_files_latest_cycle = files_in_latest_n_cycles(
                    icesat2_files, [int(c) for c in all_cycles]
                )
                is2_bbox_list.append(bbox_i)
                is2_file_list.append(icesat2_files_latest_cycle)

        is2_file_tuple = zip(is2_bbox_list, is2_file_list)

        return is2_file_tuple

    def generate_OA_parameters(self) -> list:
        """
        Get metadata from file lists in each 5*5 bbox

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

                if self.product in ["ATL07", "ATL10"]:
                    format_string = (
                        "{product:5d}-{HH:02d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{"
                        "region:02d}_{release:03d}_{version:02d}.h5"
                    )
                else:
                    format_string = (
                        "{product:5d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{"
                        "region:02d}_{release:03d}_{version:02d}.h5"
                    )
                temp = intake.source.utils.reverse_format(
                    format_string=format_string, resolved_string=fname
                )

                rgt = temp["rgt"]  # Reference Ground Track
                cycle = temp["cycle"]  # Cycle number
                f_date = str(temp["datetime"].date())  # Datetime

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
        """Make HTTP request"""
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
            A dask array containing the ICESat-2 data.
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

        except:
            beam_data = None

        if not beam_data:
            return

        data_name = "lat_lon_elev_canopy" if product == "ATL08" else "lat_lon_elev"

        sample_rate = 50 if product == "ATL06" else 20

        # iterate six beams
        beam_elev = [
            beam_data[i][data_name][::sample_rate] for i in range(6) if beam_data[i][data_name]
        ]

        if not beam_elev:
            return

        # elevation for all available beams
        OA_array = np.vstack(beam_elev)

        if OA_array.shape[0] > 0:
            OA_array = np.c_[OA_array,
                             np.full(np.size(OA_array, 0), trackId),
                             np.full(np.size(OA_array, 0), cycle)]
            OA_darr = da.from_array(OA_array, chunks=1000)

            return OA_darr

    def parallel_request_OA(self) -> da.array:
        """
        Requests elevation data from OpenAltimetry API in parallel.
        Now only supports OA_Products ['ATL06','ATL07','ATL08','ATL10','ATL12','ATL13']

        For ATL03 Photon Data, OA only supports single date request
        according to: https://openaltimetry.org/data/swagger-ui/#/Public/getATL08DataByDate,
        with geospatial limitation of 1 degree lat/lon

        Returns
        -------
        OA_data_da : dask.Array
            A dask array containing the ICESat-2 data.
        """
        print("Generating urls")

        # generate parameter lists for OA requesting
        OA_para_list = self.generate_OA_parameters()

        url_number = len(OA_para_list)

        if url_number > 200:
            answer = user_check("Too many API requests, this may take a long time, do you still want to continue: "
                                "please enter yes/no\n")

            if answer == 'yes':
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

        if self.product in ["ATL06", "ATL07", "ATL08", "ATL10", "ATL12", "ATL13"]:

            OA_da = self.parallel_request_OA()

            if OA_da is None:
                print("No data")
                return (None,) * 2

            else:

                cols = ['lat', 'lon', 'elevation', 'canopy', 'rgt', 'cycle'] if self.product == "ATL08" else ['lat',
                                                                                                              'lon',
                                                                                                              'elevation',
                                                                                                              'rgt',
                                                                                                              'cycle']
                ddf = dd.io.from_dask_array(OA_da, columns=cols).astype(
                    {"lat": "float",
                     "lon": "float",
                     "elevation": "float",
                     "rgt": "int",
                     "cycle": "int"
                     })

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
                lineplot_rgt = rasterize(
                    curve_rgt, aggregator=ds.mean("elevation")
                ).opts(width=450, height=450, cmap=["blue"])

                return map_cycle, map_rgt + lineplot_rgt

        else:
            print(
                "Oops! Elevation visualization only supports products ATL06, ATL07, ATL08, ATL10, ATL12, ATL13, "
                "please try another product."
            )
