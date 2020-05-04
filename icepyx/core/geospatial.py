import geopandas as gpd
from shapely.geometry import Polygon
 
def geodataframe(extent_type, spatial_extent, file=False):
        """
        Return a geodataframe of the spatial extent

        Examples
        --------
        >>> region_a = icepyx.Icesat2Data('ATL06',[-64, 66, -55, 72],['2019-02-22','2019-02-28'])
        >>> gdf = region_a.geodataframe()
        >>> gdf.geometry
        0    POLYGON ((-64 66, -64 72, -55 72, -55 66, -64 ...
        Name: geometry, dtype: object
        """

        if extent_type == 'bounding_box':
            boxx = [spatial_extent[0], spatial_extent[0], spatial_extent[2],\
                    spatial_extent[2], spatial_extent[0]]
            boxy = [spatial_extent[1], spatial_extent[3], spatial_extent[3],\
                    spatial_extent[1], spatial_extent[1]]
            #DevGoal: check to see that the box is actually correctly constructed; have not checked actual location of test coordinates
            gdf = gpd.GeoDataFrame(geometry=[Polygon(list(zip(boxx,boxy)))])

        #DevGoal: Currently this if/else within this elif are not tested...
        #DevGoal: the crs setting and management needs to be improved
        elif extent_type == 'polygon' and file==False:
            if isinstance(spatial_extent,str):
                spat_extent = spatial_extent.split(',')
                spatial_extent_geom = Polygon(zip(spat_extent[0::2], spat_extent[1::2]))
            else:
                spatial_extent_geom = spatial_extent
            
            gdf = gpd.GeoDataFrame(index=[0],crs={'init':'epsg:4326'}, geometry=[spatial_extent_geom])

        #DevGoal: Currently this elif isn't tested...
        elif extent_type == 'polygon' and file==True:
            gdf = gpd.read_file(spatial_extent)

        else:
            raise TypeError("Your spatial extent type (" + extent_type + ") is not an accepted input and a geodataframe cannot be constructed")

        return gdf