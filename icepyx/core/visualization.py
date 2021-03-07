# utility modules
import intake
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
from holoviews.operation.datashader import datashade, rasterize

import icepyx as ipx
import icepyx.core.geospatial as geospatial

hv.extension('bokeh')
gv.extension('bokeh')

def filelist_latestcycle(filelist, cycle_list):
    """
    Only get filelist for lastest cycle if multiple cycles are requested
    """
    if len(cycle_list) > 1:
        # for multiple repeat cycles, only request data for lastest cycle
        latest_cycle = max(cycle_list)
        new_filelist = [f for f in filelist if int(f[-14:-12]) == latest_cycle]
        return new_filelist

    else:
        return filelist


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

        # check if bounding box satisfies extent thresholds:
        # |maxx - minx| < 5 and maxy - miny < 5
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

            is2_bbox_list.append(bbox_i)
            is2_file_list.append(icesat2_files)

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

        # t uple of non-empty bbox and ICESat-2 datafiles
        filelist_tuple = self.query_icesat2_filelist()

        for bbox_i, filelist in filelist_tuple:

            for fname in filelist:

                if self.product in ['ATL07', 'ATL10']:
                    temp = intake.source.utils.reverse_format(
                        format_string="{product:5d}-{HH:02d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{"
                                      "region:02d}_{release:03d}_{version:02d}.h5",
                        resolved_string=fname,
                    )

                else:
                    temp = intake.source.utils.reverse_format(
                        format_string="{product:5d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{region:02d}_{"
                                      "release:03d}_{version:02d}.h5",
                        resolved_string=fname,
                    )

                rgt = temp['rgt']  # Reference Ground Track
                cycle = temp['cycle']  # Cycle number
                f_date = str(temp['datetime'].date())  # Datetime

                paras = [rgt, f_date, cycle, bbox_i, self.product]
                paras_list.append(paras)

        return paras_list

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
        r = requests.get(base_url, params=payload)

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

        data_name = 'lat_lon_elev'

        if product == 'ATL08':
            data_name = 'lat_lon_elev_canopy'

        # iterate six beams
        beam_elev = [beam_data[0]['beams'][i][data_name] for i in np.arange(6) if
                     beam_data[0]['beams'][i][data_name] != []]

        if not beam_elev:  # if no data
            return

        # elevation for all available beams
        OA_array = np.vstack(beam_elev)

        if OA_array.size > 0:
            # convert numpy to dask array
            OA_array = np.expand_dims(OA_array, axis=(0, 1, 2))
            OA_darr = da.from_array(OA_array, chunks=5000)

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
                    lon=(["rgt", "cycle", "bbox", "index"], lon)
                ),
                coords=dict(
                    rgt=rgt_no,
                    cycle=cycle_no,
                    index=index,
                    bbox=bbox_no
                ),
                attrs=dict(description="ICESat-2 Elevation"),

            )
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

        print('Generate parameters')

        # generate parameter lists for OA requesting
        OA_para_list = self.generate_OA_parameters()

        print('Request data from OpenAltimetry, please wait...')

        ### Parallel processing ###
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=30)
        parallel_OA_data = {pool.submit(self.request_OA_data, para_list): para_list for para_list in OA_para_list}

        requested_OA_data = []

        # for future in tqdm(concurrent.futures.as_completed(parallel_OA_data)):
        for future in tqdm(
            iterable=concurrent.futures.as_completed(parallel_OA_data),
            total=len(parallel_OA_data),
        ):
            r = future.result()
            if r is not None:
                requested_OA_data.append(r)

        try:
            # OA_data = np.vstack(requested_OA_data)
            OA_data_ds = xr.merge(list(filter(None, requested_OA_data)))
            return OA_data_ds

        except:
            pass

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

        OA_ds  = self.parallel_request_OA()
        ddf = OA_ds.to_dask_dataframe()
        ddf = ddf.repartition(npartitions=ddf.npartitions * 1000)

        print ('Plot elevation, please wait...')

        x, y = ds.utils.lnglat_to_meters(ddf.lon, ddf.lat)
        ddf_new = ddf.assign(x=x, y=y).persist()

        dset = hv.Dataset(ddf_new)
        ropts = dict(colorbar=True, tools=["hover"], width=350)
        grouped = dset.to(hv.Scatter, ['x'], vdims=['y', 'elevation'], groupby=['cycle'], dynamic=True)
        tiles = hv.element.tiles.EsriImagery().opts(xaxis=None, yaxis=None, width=500, height=500)

        return tiles * rasterize(grouped).opts(cmap="cool", cnorm="linear").opts(**ropts)