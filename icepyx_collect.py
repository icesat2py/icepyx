from icepyx import is2class as ipd

import os
import geopandas as gpd
import pandas as pd
import shutil
import sys
sys.path.append('../')
import credentials as cr
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

""" dev goal(s) on current branch:
    1. allow input of polygon coord pairs
    2. allow spatial polygon input (gpkg, shp, kml - currently kml has fiona issue?)
    3. Allow func of icepyx that will plot your select spatial parameters with mpl or cartopy or something
    """
""" user inputs passed to eventuall subset function
required: earthdata credentials, product(atl06 etc)
startDate, endDate, spatial bounds (for now bbox)
opt: outputdir, list of variables, streaming y/n"""

uid=cr.uid
pswd=cr.pswd
email=cr.email

# Input start date in yyyy-MM-dd format
start_date = '2019-08-13'
# Input start time in HH:mm:ss format
start_time = '00:00:00'
# Input end date in yyyy-MM-dd format
end_date = '2019-08-15'
# Input end time in HH:mm:ss format
end_time = '23:59:59'
""" 1 granule"""


# Input bounding box
# Input lower left longitude in decimal degrees
LL_lon = -49
# Input lower left latitude in decimal degrees
LL_lat = 68
# Input upper right longitude in decimal degrees
UR_lon = -48
# Input upper right latitude in decimal degrees
UR_lat = 69


short_name = 'ATL06'
spatial_extent = [LL_lon, LL_lat, UR_lon, UR_lat]
spatial_extent =   [-49,69,-49,68,-48.5,67,-48,68,-48,69,-49,69]

spatial_extent = 'polygons/emmons/glims_polygons.shp'
# spatial_extent = 'polygons/PineIsland/glims_polygons.shp'

date_range = [start_date,end_date]




region_a = ipd.Icesat2Data(short_name, spatial_extent, date_range)
# print(region_a.dataset)
# print(region_a.dates)
# print(region_a.start_time)
# print(region_a.end_time)
# print(region_a.dataset_version)
# print(region_a.spatial_extent)
# print(region_a.geodataframe)
# region_a.geodataframe
# region_a.vizualize_spatial_extent

#

# region_a.build_CMR_params()
# print(region_a.avail_granules())


# earthdata_uid = uid
# email = email
# session=region_a.earthdata_login(earthdata_uid, email)
#
#
# region_a.build_reqconfig_params('download', page_size=9)
# region_a.reqparams
# region_a.order_granules(session)
# region_a.orderIDs
# path = './Outputs'
# region_a.download_granules(session, path)
