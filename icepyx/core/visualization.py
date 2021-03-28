"""
Interactive visualization of spatial extent and ICESat-2 elevations
"""
import intake
import backoff
import requests
import numpy as np
from shapely.geometry import Polygon
from itertools import compress
import concurrent.futures
from tqdm import tqdm
import xarray as xr
import dask.array as da
import datashader as ds
import geoviews as gv
import holoviews as hv
from holoviews.operation.datashader import rasterize

import icepyx as ipx
import icepyx.core.geospatial as geospatial

hv.extension('bokeh')
gv.extension('bokeh')


def files_in_latest_n_cycles(files, cycles, n=1):
    """
    Get list of file names in latest n cycles
    """
    if n == 1:
        latest_cycle = max(cycles)
        viz_file_list = [f for f in files if int(f.rsplit('_')[-3][4:6]) == latest_cycle]
        return viz_file_list

    elif n > 1:
        if len(cycles) >= n:
            viz_cycle_list = [max(cycles)-i for i in np.arange(n)]
        else:
            viz_cycle_list = cycles
        viz_file_list = [f for f in files if int(f.rsplit('_')[-3][4:6]) in viz_cycle_list]
        return viz_file_list

    else:
        raise Exception('Wrong n value')


class Visualize:

    def __init__(self, product, bbox, date_range):
        self.product = product
        self.bbox = bbox
        self.date_range = date_range

    def grid_bbox(self, binsize=5):
        """
        Split bounding box into 5 x 5 grids
        when latitude/longitude range exceeds the default OpenAltimetry 5*5 degree spatial limits
        :return: a list of 5*5 degree bbox
        """
        lonmin = self.bbox[0]
        latmin = self.bbox[1]
        lonmax = self.bbox[2]
        latmax = self.bbox[3]

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
                    bbox_ij = [lonxv[i, j], latyv[i, j], lonxv[i + 1, j + 1], latyv[i + 1, j + 1]]

                    if bbox_ij[2] > lonmax:
                        bbox_ij[2] = lonmax

                    if bbox_ij[3] > latmax:
                        bbox_ij[3] = latmax

                    bbox_list.append(bbox_ij)

            return bbox_list

        else:
            return [self.bbox]

    def query_icesat2_filelist(self):
        """
        Query list of ICESat-2 files based on splitted bbox
        :return: tuples of non-empty bbox list and corresponding ICESat-2 file lists
        """
        # a list of 5*5 bounding boxes
        bbox_list = self.grid_bbox()

        is2_bbox_list = []
        is2_file_list = []

        for bbox_i in bbox_list:
            ### NEED Change for Track & Cycle Implementation
            region = ipx.Query(self.product, bbox_i, self.date_range)
            icesat2_files = region.avail_granules(ids=True, cycles=True, tracks=True)[0]

            if not icesat2_files:
                continue
            else:
                icesat2_files_latest_cycle = files_in_latest_n_cycles(icesat2_files, [int(c) for c in region.cycles])
                is2_bbox_list.append(bbox_i)
                is2_file_list.append(icesat2_files_latest_cycle)

        filelist_tuple = zip(is2_bbox_list, is2_file_list)

        return filelist_tuple

    def generate_OA_parameters(self):
        """
        Get metadata from file lists in each 5*5 bbox
        :return: a list of parameters for OpenAltimetry API query, including
                 RGT, cycle number, datetime, bounding box, product name
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

                rgt = temp['rgt']  # Reference Ground Track
                cycle = temp['cycle']  # Cycle number
                f_date = str(temp['datetime'].date())  # Datetime

                paras = [rgt, f_date, cycle, bbox_i, self.product]
                paras_list.append(paras)

        return paras_list

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.Timeout,
                           requests.exceptions.ConnectionError,
                           requests.exceptions.ChunkedEncodingError),
                          max_tries=5)
    def make_request(self, base_url, payload):
        """Make HTTP request"""
        return requests.get(base_url, params=payload)

    def request_OA_data(self, paras):
        """
        Request data from OpenAltimetry based on API:
        https://openaltimetry.org/data/swagger-ui/#/

        :param paras: one parameter list for OpenAltimetry API request
        :return: xarray dataset
        """

        base_url = 'https://openaltimetry.org/data/api/icesat2/level3a'

        trackId = paras[0]
        Date = paras[1]
        cycle = paras[2]
        bbox = paras[3]
        product = paras[4]

        # Generate API
        payload = {'product': product.lower(),
                   'endDate': Date,
                   'minx': str(bbox[0]),
                   'miny': str(bbox[1]),
                   'maxx': str(bbox[2]),
                   'maxy': str(bbox[3]),
                   'trackId': trackId,
                   'outputFormat': 'json'}  # default return all six beams

        # request OpenAltimetry
        r = self.make_request(base_url, payload)

        # get elevation data
        elevation_data = r.json()

        # length of file list
        file_len = len(elevation_data['data'])

        # file index satisfies acquisition time from data file
        idx = [elevation_data['data'][i]['date'] == Date for i in np.arange(file_len)]

        # get data we need
        beam_data = list(compress(elevation_data['data'], idx))

        if not beam_data:
            return

        data_name = "lat_lon_elev_canopy" if product == "ATL08" else "lat_lon_elev"

        # iterate six beams, sampling rate: 1/20
        beam_elev = [beam_data[0]['beams'][i][data_name][::20] for i in np.arange(6) if
                     beam_data[0]['beams'][i][data_name] != []]

        if not beam_elev:
            return

        # elevation for all available beams
        OA_array = np.vstack(beam_elev)

        if OA_array.size > 0:
            # convert numpy to dask array
            OA_array = np.expand_dims(OA_array, axis=(0, 1, 2))
            OA_darr = da.from_array(OA_array, chunks=1000)

            elevation = OA_darr[:, :, :, :, 2]
            lat = OA_darr[:, :, :, :, 0]
            lon = OA_darr[:, :, :, :, 1]
            index = np.arange(elevation.shape[3])
            bbox_no = [str(bbox)]
            rgt_no = [trackId]
            cycle_no = [cycle]

            # create xarray dataset
            OA_ds = xr.Dataset(
                data_vars=dict(
                    elevation=(["rgt", "cycle", "bbox", "index"], elevation),
                    lat=(["rgt", "cycle", "bbox", "index"], lat),
                    lon=(["rgt", "cycle", "bbox", "index"], lon)),
                coords=dict(
                    rgt=rgt_no,
                    cycle=cycle_no,
                    index=index,
                    bbox=bbox_no),
                attrs=dict(description="ICESat-2 Elevation"))

            return OA_ds

    def parallel_request_OA(self):
        """
        Requesting elevation data from OpenAltimetry API in parallel
        Now only supports OA_Products ['ATL06','ATL07','ATL08','ATL10','ATL12','ATL13']

        For ATL03 Photon Data, OA only supports single date request
        according to: https://openaltimetry.org/data/swagger-ui/#/Public/getATL08DataByDate,
        with geospatial limitation of 1 degree lat/lon

        :return: all requested ICESat-2 elevation in xarray dataset
        """
        print('Generating urls')

        # generate parameter lists for OA requesting
        OA_para_list = self.generate_OA_parameters()

        print('Sending request to OpenAltimetry, please wait...')

        # Parallel processing
        requested_OA_data = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(OA_para_list)) as executor:
            parallel_OA_data = {executor.submit(self.request_OA_data, para): para for para in OA_para_list}

            for future in tqdm(
                    iterable=concurrent.futures.as_completed(parallel_OA_data),
                    total=len(parallel_OA_data),
            ):
                r = future.result()
                if r is not None:
                    requested_OA_data.append(r)

        requested_OA_data_filtered = list(filter(None, requested_OA_data))

        if not requested_OA_data_filtered:
            return
        else:
            OA_data_ds = xr.merge(requested_OA_data_filtered)
            return OA_data_ds

    def visualize_extent(self):
        """Show bounding box extent set by users"""
        region = ipx.Query(self.product, self.bbox, self.date_range)
        gdf = geospatial.geodataframe(region.extent_type, region._spat_extent)
        line_geoms = Polygon(gdf['geometry'][0]).boundary
        bbox_poly = gv.Path(line_geoms).opts(color="red", line_color="red")
        tile = gv.tile_sources.EsriImagery.opts(width=500, height=500)
        return tile * bbox_poly

    def visualize_elevation(self):
        """
        Visualize elevation requested from OpenAltimetry API using datashader based on cycles
        https://holoviz.org/tutorial/Large_Data.html
        """

        if self.product in ['ATL06', 'ATL07', 'ATL08', 'ATL10', 'ATL12', 'ATL13']:

            OA_ds = self.parallel_request_OA()

            if OA_ds is None:
                print('No data')

            else:
                ddf = OA_ds.to_dask_dataframe().astype({'lat': 'float', 'lon': 'float','elevation': 'float'})

                print('Plot elevation, please wait...')

                x, y = ds.utils.lnglat_to_meters(ddf.lon, ddf.lat)
                ddf_new = ddf.assign(x=x, y=y).persist()
                dset = hv.Dataset(ddf_new)

                raster_cycle = dset.to(hv.Points, ['x', 'y'], ['elevation'], groupby=['cycle'], dynamic=True)
                raster_rgt = dset.to(hv.Points, ['x', 'y'], ['elevation'], groupby=['rgt'], dynamic=True)
                curve_rgt = dset.to(hv.Scatter, ['lat'], ['elevation'], groupby=['rgt'], dynamic=True)

                tiles = hv.element.tiles.EsriImagery().opts(xaxis=None, yaxis=None, width=450, height=450)
                map_cycle = tiles * rasterize(raster_cycle, aggregator=ds.mean('elevation')).opts(colorbar=True,
                                                                                                  tools=['hover'])
                map_rgt = tiles * rasterize(raster_rgt, aggregator=ds.mean('elevation')).opts(colorbar=True,
                                                                                              tools=['hover'])
                lineplot_rgt = rasterize(curve_rgt, aggregator=ds.mean('elevation')).opts(width=450, height=450, cmap=['blue'])

                return map_cycle, map_rgt + lineplot_rgt, OA_ds

        else:
            print('Oops! Elevation visualization only supports products [ATL06, ATL07, ATL08, ATL10, ATL12, ATL13], '
                  'please try another data product.')
