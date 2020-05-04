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
            raise TypeError("Your spatial extent type is not an accepted input and a geodataframe cannot be constructed")
            #DevNote: can't get test for this else to pass if print the extent_type in the string...
            # raise TypeError("Your spatial extent type (" + extent_type + ") is not an accepted input and a geodataframe cannot be constructed")

        return gdf


        {'feed': {'updated': '2020-05-04T20:23:21.770Z', 'id': 'https://cmr.earthdata.nasa.gov:443/search/collections.json?short_name=ATL06', 'title': 'ECHO dataset metadata', 'entry': [{'processing_level_id': 'Level 3', 'boxes': ['-90 -180 90 180'], 'time_start': '2018-10-14T00:00:00.000Z', 'version_id': '001', 'dataset_id': 'ATLAS/ICESat-2 L3A Land Ice Height V001', 'has_spatial_subsetting': True, 'has_transforms': False, 'associations': {'services': ['S1568899363-NSIDC_ECS', 'S1613689509-NSIDC_ECS', 'S1613669681-NSIDC_ECS']}, 'has_variables': True, 'data_center': 'NSIDC_ECS', 'short_name': 'ATL06', 'organizations': ['NASA NSIDC DAAC', 'NASA/GSFC/EOS/ESDIS'], 'title': 'ATLAS/ICESat-2 L3A Land Ice Height V001', 'coordinate_system': 'CARTESIAN', 'summary': 'This data set (ATL06) provides geolocated, land-ice surface heights (above the WGS 84 ellipsoid, ITRF2014 reference frame), plus ancillary parameters that can be used to interpret and assess the quality of the height estimates. The data were acquired by the Advanced Topographic Laser Altimeter System (ATLAS) instrument on board the Ice, Cloud and land Elevation Satellite-2 (ICESat-2) observatory.', 'orbit_parameters': {'swath_width': '36.0', 'period': '94.29', 'inclination_angle': '92.0', 'number_of_orbits': '0.071428571', 'start_circular_latitude': '0.0'}, 'id': 'C1511847675-NSIDC_ECS', 'has_formats': True, 'original_format': 'ISO19115', 'archive_center': 'NASA NSIDC DAAC', 'has_temporal_subsetting': True, 'browse_flag': False, 'online_access_flag': True, 'links': [{'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://n5eil01u.ecs.nsidc.org/ATLAS/ATL06.001/'}, {'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://search.earthdata.nasa.gov/search/granules?p=C1511847675-NSIDC_ECS&m=-87.87967837686685!9.890967019347585!1!1!0!0%2C2&tl=1542476530!4!!&q=atl06&ok=atl06'}, {'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://openaltimetry.org/'}, {'rel': 'http://esipfed.org/ns/fedsearch/1.1/metadata#', 'hreflang': 'en-US', 'href': 'https://doi.org/10.5067/ATLAS/ATL06.001'}, {'rel': 'http://esipfed.org/ns/fedsearch/1.1/documentation#', 'hreflang': 'en-US', 'href': 'https://doi.org/10.5067/ATLAS/ATL06.001'}]}, {'processing_level_id': 'Level 3', 'boxes': ['-90 -180 90 180'], 'time_start': '2018-10-14T00:00:00.000Z', 'version_id': '002', 'dataset_id': 'ATLAS/ICESat-2 L3A Land Ice Height V002', 'has_spatial_subsetting': True, 'has_transforms': False, 'associations': {'services': ['S1568899363-NSIDC_ECS', 'S1613669681-NSIDC_ECS', 'S1613689509-NSIDC_ECS']}, 'has_variables': True, 'data_center': 'NSIDC_ECS', 'short_name': 'ATL06', 'organizations': ['NASA NSIDC DAAC', 'NASA/GSFC/EOS/ESDIS'], 'title': 'ATLAS/ICESat-2 L3A Land Ice Height V002', 'coordinate_system': 'CARTESIAN', 'summary': 'This data set (ATL06) provides geolocated, land-ice surface heights (above the WGS 84 ellipsoid, ITRF2014 reference frame), plus ancillary parameters that can be used to interpret and assess the quality of the height estimates. The data were acquired by the Advanced Topographic Laser Altimeter System (ATLAS) instrument on board the Ice, Cloud and land Elevation Satellite-2 (ICESat-2) observatory.', 'orbit_parameters': {'swath_width': '36.0', 'period': '94.29', 'inclination_angle': '92.0', 'number_of_orbits': '0.071428571', 'start_circular_latitude': '0.0'}, 'id': 'C1631076765-NSIDC_ECS', 'has_formats': True, 'original_format': 'ISO19115', 'archive_center': 'NASA NSIDC DAAC', 'has_temporal_subsetting': True, 'browse_flag': False, 'online_access_flag': True, 'links': [{'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://n5eil01u.ecs.nsidc.org/ATLAS/ATL06.002/'}, {'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://search.earthdata.nasa.gov/search/granules?p=C1631076765-NSIDC_ECS&q=atl06%20v002&m=-113.62703547966265!-24.431396484375!0!1!0!0%2C2&tl=1556125020!4'}, {'length': '0.0KB', 'rel': 'http://esipfed.org/ns/fedsearch/1.1/data#', 'hreflang': 'en-US', 'href': 'https://openaltimetry.org/'}, {'rel': 'http://esipfed.org/ns/fedsearch/1.1/metadata#', 'hreflang': 'en-US', 'href': 'https://doi.org/10.5067/ATLAS/ATL06.002'}, {'rel': 'http://esipfed.org/ns/fedsearch/1.1/documentation#', 'hreflang': 'en-US', 'href': 'https://doi.org/10.5067/ATLAS/ATL06.002'}]}]}}