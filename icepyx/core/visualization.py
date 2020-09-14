# utility modules
import glob
import os
import sys
import re
import intake
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Point
from itertools import compress
import concurrent.futures
import matplotlib.pyplot as plt
import holoviews as hv
import dask.array as da
import dask.dataframe as dd
import hvplot.dask  # adds hvplot method to dask objects
import datashader as ds
from holoviews import opts
from holoviews.operation.datashader import datashade, rasterize
#from holoviews.element.tiles import EsriImager
hv.extension('bokeh', "matplotlib") 

import icepyx.core.geospatial as geospatial

def filelist_latestcycle(filelist, cycle_list):
    """
    Only get filelist for lastest cycle if multiple cycles are requested
    """
    if len(cycle_list) >1:
    # for multiple repeat cycles, only request data for lastest cycle
        latest_cycle = max(cycle_list)
        new_filelist = [f for f in filelist if int(f[-14:-12])==latest_cycle]
        return new_filelist

    else: # only one cycle
        return filelist

class Visualize:
    
    """
    Visualize data extent and the elevation distribution by requesting OpenAltimetry API before downloading data from NSIDC
    """
    
    def __init__(self, filelist, bbox, product):
        
        self.filelist = filelist # filelist requested from icepyx Query object
        self.bbox = bbox # Input bounding box 
        self.product = product # Input ICESat-2 product

    def file_meta(self,bbox_i):
        """
        Obtain metadata from filename list with bounding box satistifying OA 5 degree threshold
        Return:
            para_lists
            
        ### NEED CHANGE HERE ###
        """

        para_lists = [] # list of parameters for API query

        for fname in self.filelist:

            if self.product in ['ATL07', 'ATL10']:
                temp = intake.source.utils.reverse_format(
                        format_string="{product:5d}-{HH:02d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{region:02d}_{release:03d}_{version:02d}.h5",
                        resolved_string=fname,
                    )

            else: 
                temp = intake.source.utils.reverse_format(
                        format_string="{product:5d}_{datetime:%Y%m%d%H%M%S}_{rgt:04d}{cycle:02d}{region:02d}_{release:03d}_{version:02d}.h5",
                        resolved_string=fname,
                    )

            rgt = temp['rgt']
            cycle = temp['cycle']
            f_date = str(temp['datetime'].date())

            paras = [rgt, f_date, cycle, bbox_i, self.product]
            para_lists.append(paras)

        return para_lists

    def grid_bbox(self, binsize = 5):
        """Split bounding box into smaller grids if latitude/longitude range exceed the default 5 degree limit of OpenAltimetry """

        lonmin = self.bbox[0]
        latmin = self.bbox[1]
        lonmax = self.bbox[2]
        latmax = self.bbox[3]

        lonx = np.arange(lonmin, lonmax + binsize, binsize)
        laty = np.arange(latmin, latmax + binsize, binsize) 
        lonxv, latyv = np.meshgrid(lonx, laty)

        ydim, xdim = lonxv.shape 

        bbox_list = []
        for i in np.arange(0,ydim-1): 
            for j in np.arange(0,xdim-1):
                # iterate grid for bounding box
                bbox_ij = [lonxv[i,j], latyv[i,j], lonxv[i+1,j+1], latyv[i+1,j+1]]

                if bbox_ij[2] > lonmax:
                    bbox_ij[2] = lonmax

                if bbox_ij[3] > latmax:
                    bbox_ij[3] = latmax

                bbox_list.append(bbox_ij)

        return bbox_list

    def generate_OA_paras(self):
        """Generate parameter lists for OpenAltimetry API"""

        # spatial extent check and grid bbox
        lonmax = self.bbox[2]
        lonmin = self.bbox[0]
        latmax = self.bbox[3]
        latmin = self.bbox[1]

        # check if bounding box satisfies extent thresholds: |maxx - minx| < 5 and maxy - miny < 5 ###
        extent_flag = ((lonmax - lonmin) > 5 ) or ((latmax - latmin) > 5 ) 

        if extent_flag:
            #print ('spatial extent exceeds OA 5 degree threshold, spliting bbox...')
            bbox_list = self.grid_bbox()
            paras = [self.file_meta(bbox_i) for bbox_i in bbox_list]
            para_lists = [para_list for sublists in paras for para_list in sublists]
        else:
            #print ('spatial extent satifies OA 5 degree threshold, generating data...')
            bbox_list = self.bbox
            para_lists = self.file_meta(bbox_list)

        return para_lists

    def request_OA_elev(self, paralist):
        """
        Request data from OpenAltimetry based on API: https://openaltimetry.org/data/swagger-ui/#/
        Return:
            OA_array: numpy array for all beams of one RGT in paralist
        """
        base_url = 'https://openaltimetry.org/data/api/icesat2/level3a'

        points = [] # store all beam data for one RGT

        trackId,Date,cycle,bbox,product = paralist[0], paralist[1], paralist[2], paralist[3], paralist[4]

        # iterate all six beams 
        # for beam in beamlist:
        # Generate API
        payload =  {'product':product.lower(),
                    'endDate': Date,
                    'minx':str(bbox[0]),
                    'miny':str(bbox[1]),
                    'maxx':str(bbox[2]),
                    'maxy':str(bbox[3]),
                    'trackId': trackId,
                    'outputFormat':'json'} # default return all six beams

        # request OpenAltimetry
        r = requests.get(base_url, params=payload)

        # get elevation data
        elevation_data = r.json()

        # length of file list
        file_len = len(elevation_data['data'])

        # file index satifies aqusition time from data file
        idx = [elevation_data['data'][i]['date'] == Date for i in np.arange(file_len)]

        # get data we need
        beam_data = list(compress(elevation_data['data'], idx))

        if not beam_data:
            return 

        data_name = 'lat_lon_elev'

        if product == 'ATL08':
            data_name = 'lat_lon_elev_canopy'

        # elevation array by iterating all six beams
        beam_elev = [beam_data[0]['beams'][i][data_name] for i in np.arange(6) if beam_data[0]['beams'][i][data_name] != []]

        if not beam_elev: # check if no data 
            return  

        OA_array = np.vstack(beam_elev)

        if OA_array.size > 0:
            return OA_array


    def parallel_request_OA(self):
        """ 
        Requesting elevation data from OpenAltimetry API in parallel
        Only supports OA_Products ['ATL06','ATL07','ATL08','ATL10','ATL12','ATL13']
        For ATL03 Photon Data, OA only supports single date request according to: https://openaltimetry.org/data/swagger-ui/#/Public/getATL08DataByDate, 
        and the geospatial limitation is 1 degree in both lat/lon
        
        Return: 
            OA_data: dataframe containing all requested OA datasets
        """

        print ('Requesting data for elevation visualization, please wait...')

        # generate parameter lists for OA requesting
        para_lists = self.generate_OA_paras()

        ### Parallel processing ###
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=30)
        parallel_OA_data = {pool.submit(self.request_OA_elev,paralist): paralist for paralist in para_lists}

        requested_OA_data=[]

        for future in concurrent.futures.as_completed(parallel_OA_data):
            r = future.result()
            if r is not None:
                requested_OA_data.append(r)

        try:
            OA_data = np.vstack(requested_OA_data) 
            return OA_data

        except:
            pass

    def visualize_elevation_matplotlib(self, OA_data):
        """Visualize elevation data requested from OpenAltimetry API"""

        # convert into geodataframe
        geometry = gpd.points_from_xy(x=OA_data[:,1], y=OA_data[:,0])     
        gdf_OA = gpd.GeoDataFrame({'lat':OA_data[:,0],
                                   'lon':OA_data[:,1],
                                   'h':OA_data[:,2]}, 
                                  geometry=geometry, 
                                  crs=CRS('EPSG:4326'))

        # plot elevation
        fig= plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        cs = plt.scatter(gdf_OA['geometry'].x, gdf_OA['geometry'].y, c=gdf_OA['h'], vmin=gdf_OA['h'].min(),
                         vmax=gdf_OA['h'].max(), cmap='RdYlBu_r', s=15, label='OpenAltimetry')

        colorbar = fig.colorbar(cs, ax=ax)
        colorbar.set_label('Elevation(m)', fontsize=15)
        colorbar.ax.tick_params(labelsize=15)

        plt.tight_layout()
        plt.show()

    def visualize_elevations_holoview(self, OA_data):
        """
        Visualize elevation data requested from OpenAltimetry API
        https://holoviz.org/tutorial/Large_Data.html
        https://datashader.org/getting_started/Interactivity.html
        https://towardsdatascience.com/data-visualization-with-python-holoviz-plotting-4848e905f2c0
        """
        # convert array into dask dataframe
        oa_array = da.from_array(OA_data, chunks=(5000, 3))
        oa_df = dd.from_dask_array(oa_array, columns=['lat', 'lon', 'h'])
        x, y = ds.utils.lnglat_to_meters(oa_df.lon, oa_df.lat)
        ddf = oa_df.assign(x=x, y=y).persist()
        points = hv.Points(ddf, ['x', 'y'])
        tiles = hv.element.tiles.EsriImagery().opts(xaxis=None, yaxis=None, width=700, height=500)
        return tiles * datashade(points)

    def visualize_spatial_extent(self, extent_type, spat_extent):
        """Default visualization of spatial extent"""

        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        f, ax = plt.subplots(1, figsize=(12, 6))
        world.plot(ax=ax, facecolor="lightgray", edgecolor="gray")
        geospatial.geodataframe(extent_type, spat_extent).plot(
            ax=ax, color="#FF8C00", alpha=0.7
        )
        plt.show()
    