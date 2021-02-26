import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import h5py
import scipy
from astropy.time import Time
# from icepyx import icesat2data as ipd

def getATL03(f,beam):
    # height of each received photon, relative to the WGS-84 ellipsoid (with some, not all corrections applied, see background info above)
    heights=f[beam]['heights']['h_ph'][:]
    # latitude (decimal degrees) of each received photon
    lats=f[beam]['heights']['lat_ph'][:]
    # longitude (decimal degrees) of each received photon
    lons=f[beam]['heights']['lon_ph'][:]
    # seconds from ATLAS Standard Data Product Epoch. use the epoch parameter to convert to gps time
    dt=f[beam]['heights']['delta_time'][:]
    # confidence level associated with each photon event
    # -2: TEP
    # -1: Events not associated with a specific surface type
    #  0: noise
    #  1: buffer but algorithm classifies as background
    #  2: low
    #  3: medium
    #  4: high
    # Surface types for signal classification confidence
    # 0=Land; 1=Ocean; 2=SeaIce; 3=LandIce; 4=InlandWater    
    conf=f[beam]['heights']['signal_conf_ph'][:,2] #choose column 2 for confidence of sea ice photons
    # number of ATL03 20m segments
    n_seg, = f[beam]['geolocation']['segment_id'].shape
    # first photon in the segment (convert to 0-based indexing)
    Segment_Index_begin = f[beam]['geolocation']['ph_index_beg'][:] - 1
    # number of photon events in the segment
    Segment_PE_count = f[beam]['geolocation']['segment_ph_cnt'][:]
    # along-track distance for each ATL03 segment
    Segment_Distance = f[beam]['geolocation']['segment_dist_x'][:]
    # along-track distance (x) for photon events
    x_atc = np.copy(f[beam]['heights']['dist_ph_along'][:])
    # cross-track distance (y) for photon events
    y_atc = np.copy(f[beam]['heights']['dist_ph_across'][:])

    for j in range(n_seg):
        # index for 20m segment j
        idx = Segment_Index_begin[j]
        # number of photons in 20m segment
        cnt = Segment_PE_count[j]
        # add segment distance to along-track coordinates
        x_atc[idx:idx+cnt] += Segment_Distance[j]
    df03=pd.DataFrame({'lats':lats,'lons':lons,'x':x_atc,'y':y_atc,'heights':heights,'dt':dt,'conf':conf})
    return df03

def getATL07(f,beam):
    lats = f[beam+'/sea_ice_segments/latitude'][:]
    lons = f[beam+'/sea_ice_segments/longitude'][:]
    dt = f[beam+'/sea_ice_segments/delta_time'][:]
    seg_x = f[beam+'/sea_ice_segments/seg_dist_x'][:]
    heights = f[beam+'/sea_ice_segments/heights/height_segment_height'][:]
    conf = f[beam+'/sea_ice_segments/heights/height_segment_confidence'][:]
    stype = f[beam+'/sea_ice_segments/heights/height_segment_type'][:]
    ssh_flag = f[beam+'/sea_ice_segments/heights/height_segment_ssh_flag'][:]
    gauss = f[beam+'/sea_ice_segments/heights/height_segment_w_gaussian'][:]
    photon_rate = f[beam+'/sea_ice_segments/stats/photon_rate'][:]
    cloud = f[beam+'/sea_ice_segments/stats/cloud_flag_asr'][:]
    mss = f[beam+'/sea_ice_segments/geophysical/height_segment_mss'][:]
    ocean_tide = f[beam+'/sea_ice_segments/geophysical/height_segment_ocean'][:]
    lpe_tide = f[beam+'/sea_ice_segments/geophysical/height_segment_lpe'][:]
    ib = f[beam+'/sea_ice_segments/geophysical/height_segment_ib'][:]
    df07=pd.DataFrame({'lats':lats,'lons':lons,'heights':heights,'dt':dt,'conf':conf,'stype':stype,'ssh_flag':ssh_flag,     'gauss':gauss,'photon_rate':photon_rate,'cloud':cloud,'mss':mss,'ocean':ocean_tide,'lpe':lpe_tide,'ib':ib})
    return df07





#--------- READERS COPIED FROM 2019 HACKWEEK TUTORIALS (not including the dictionary/xarray readers) -----

def getATL03data(fileT, numpyout=False, beam='gt1l'):
    """ Pandas/numpy ATL03 reader
    Written by Alek Petty, June 2018 (alek.a.petty@nasa.gov)
    I've picked out the variables from ATL03 I think are of most interest to 
    sea ice users, but by no means is this an exhastive list. 
    See the xarray or dictionary readers to load in the more complete ATL03 dataset
    or explore the hdf5 files themselves (I like using the app Panpoly for this) to 
    see what else you might want
    
    Args:
        fileT (str): File path of the ATL03 dataset
        numpy (flag): Binary flag for outputting numpy arrays (True) or pandas dataframe (False)
        beam (str): ICESat-2 beam (the number is the pair, r=strong, l=weak)
        
    returns:
        either: select numpy arrays or a pandas dataframe
    """
    
    # Open the file
    try:
        ATL03 = h5py.File(fileT, 'r')
    except:
        'Not a valid file'
        
    lons=ATL03[beam+'/heights/lon_ph'][:]
    lats=ATL03[beam+'/heights/lat_ph'][:]
    
    #  Number of seconds since the GPS epoch on midnight Jan. 6, 1980 
    delta_time=ATL03[beam+'/heights/delta_time'][:] 
    
    # #Add this value to delta time parameters to compute the full gps_seconds
    atlas_epoch=ATL03['/ancillary_data/atlas_sdp_gps_epoch'][:] 
    
    # Conversion of delta_time to a calendar date
    # This function seems pretty convoluted but it works for now..
    # I'm sure there is a simpler function we can use here instead.
    temp = ut.convert_GPS_time(atlas_epoch[0] + delta_time, OFFSET=0.0)
    
    # Express delta_time relative to start time of granule
    delta_time_granule=delta_time-delta_time[0]

    year = temp['year'][:].astype('int')
    month = temp['month'][:].astype('int')
    day = temp['day'][:].astype('int')
    hour = temp['hour'][:].astype('int')
    minute = temp['minute'][:].astype('int')
    second = temp['second'][:].astype('int')
    
    dFtime=pd.DataFrame({'year':year, 'month':month, 'day':day, 
                        'hour':hour, 'minute':minute, 'second':second})
    
    
    # Primary variables of interest
    
    # Photon height
    heights=ATL03[beam+'/heights/h_ph'][:]
    print(heights.shape)
    
    # Flag for signal confidence
    # column index:  0=Land; 1=Ocean; 2=SeaIce; 3=LandIce; 4=InlandWater
    # values:
        #-- -1: Events not associated with a specific surface type
        #--  0: noise
        #--  1: buffer but algorithm classifies as background
        #--  2: low
        #--  3: medium
        #--  4: high
    signal_confidence=ATL03[beam+'/heights/signal_conf_ph'][:,2] 
    
    # Add photon rate, background rate etc to the reader here if we want
    
    ATL03.close()
    
    
    
    dF = pd.DataFrame({'heights':heights, 'lons':lons, 'lats':lats,
                       'signal_confidence':signal_confidence, 
                       'delta_time':delta_time_granule})
    
    # Add the datetime string
    dFtimepd=pd.to_datetime(dFtime)
    dF['datetime'] = pd.Series(dFtimepd, index=dF.index)
    
    # Filter out high elevation values 
    #dF = dF[(dF['signal_confidence']>2)]
    # Reset row indexing
    #dF=dF.reset_index(drop=True)
    return dF
    
    # Or return as numpy arrays 
    # return along_track_distance, heights
    
    
def getATL07data(fileT, numpy=False, beamNum=1, maxElev=1e6):
    """ Pandas/numpy ATL07 reader
    Written by Alek Petty, June 2018 (alek.a.petty@nasa.gov)
    I've picked out the variables from ATL07 I think are of most interest to sea ice users, 
    but by no means is this an exhastive list. 
    See the xarray or dictionary readers to load in the more complete ATL07 dataset
    or explore the hdf5 files themselves (I like using the app Panpoly for this) to see what else 
    you might want
    
    Args:
        fileT (str): File path of the ATL07 dataset
        numpy (flag): Binary flag for outputting numpy arrays (True) or pandas dataframe (False)
        beamNum (int): ICESat-2 beam number (1 to 6)
        maxElev (float): maximum surface elevation to remove anomalies
    returns:
        either: select numpy arrays or a pandas dataframe
        
    Updates:
        V3 (June 2018) added observatory orientation flag, read in the beam number, not the string
        V2 (June 2018) used astropy to more simply generate a datetime instance form the gps time
    """
    
    # Open the file
    try:
        ATL07 = h5py.File(fileT, 'r')
    except:
        return 'Not a valid file'
    
    #flag_values: 0, 1, 2; flag_meanings : backward forward transition
    orientation_flag=ATL07['orbit_info']['sc_orient'][:]
    
    if (orientation_flag==0):
        print('Backward orientation')
        beamStrs=['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r']
                
    elif (orientation_flag==1):
        print('Forward orientation')
        beamStrs=['gt3r', 'gt3l', 'gt2r', 'gt2l', 'gt1r', 'gt1l']
        
    elif (orientation_flag==2):
        print('Transitioning, do not use for science!')
    
    beamStr=beamStrs[beamNum-1]
    print(beamStr)
    
    lons=ATL07[beamStr+'/sea_ice_segments/longitude'][:]
    lats=ATL07[beamStr+'/sea_ice_segments/latitude'][:]
    
    # Along track distance 
    # I removed the first point so it's distance relative to the start of the beam
    along_track_distance=ATL07[beamStr+'/sea_ice_segments/seg_dist_x'][:] - ATL07[beamStr+'/sea_ice_segments/seg_dist_x'][0]
    # Height segment ID (10 km segments)
    height_segment_id=ATL07[beamStr+'/sea_ice_segments/height_segment_id'][:] 
    # Number of seconds since the GPS epoch on midnight Jan. 6, 1980 
    delta_time=ATL07[beamStr+'/sea_ice_segments/delta_time'][:] 
    # Add this value to delta time parameters to compute full gps time
    atlas_epoch=ATL07['/ancillary_data/atlas_sdp_gps_epoch'][:] 

    leapSecondsOffset=37
    gps_seconds = atlas_epoch[0] + delta_time - leapSecondsOffset
    # Use astropy to convert from gps time to datetime
    tgps = Time(gps_seconds, format='gps')
    tiso = Time(tgps, format='datetime')
    
    # Primary variables of interest
    
    # Beam segment height
    elev=ATL07[beamStr+'/sea_ice_segments/heights/height_segment_height'][:]
    # Flag for potential leads, 0=sea ice, 1 = sea surface
    ssh_flag=ATL07[beamStr+'/sea_ice_segments/heights/height_segment_ssh_flag'][:] 
    
    #Quality metrics for each segment include confidence level in the surface height estimate, 
    # which is based on the number of photons, the background noise rate, and the error measure provided by the surface-finding algorithm.
    # Height quality flag, 1 for good fit, 0 for bad
    quality=ATL07[beamStr+'/sea_ice_segments/heights/height_segment_quality'][:] 
    
    elev_rms = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_rms'][:] #RMS difference between modeled and observed photon height distribution
    seg_length = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_length_seg'][:] # Along track length of segment
    height_confidence = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_confidence'][:] # Height segment confidence flag
    reflectance = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_asr_calc'][:] # Apparent surface reflectance
    ssh_flag = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_ssh_flag'][:] # Flag for potential leads, 0=sea ice, 1 = sea surface
    seg_type = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_type'][:] # 0 = Cloud covered
    gauss_width = ATL07[beamStr+'/sea_ice_segments/heights/height_segment_w_gaussian'][:] # Width of Gaussian fit

    # Geophysical corrections
    # NOTE: All of these corrections except ocean tides, DAC, 
    # and geoid undulations were applied to the ATL03 photon heights.
    
    # AVISO dynamic Atmospheric Correction (DAC) including inverted barometer (IB) effect (±5cm)
    dac = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_dac'][:] 
    # Solid Earth Tides (±40 cm, max)
    earth = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_earth'][:]
    # Geoid (-105 to +90 m, max)
    geoid = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_geoid'][:] 
    # Local displacement due to Ocean Loading (-6 to 0 cm)
    loadTide = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_load'][:] 
    # Ocean Tides including diurnal and semi-diurnal (harmonic analysis), 
    # and longer period tides (dynamic and self-consistent equilibrium) (±5 m)
    oceanTide = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_ocean'][:]
    # Deformation due to centrifugal effect from small variations in polar motion 
    # (Solid Earth Pole Tide) (±1.5 cm, the ocean pole tide ±2mm amplitude is considered negligible)
    poleTide = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_pole'][:] 
    # Mean sea surface (±2 m)
    # Taken from ICESat and CryoSat-2, see Kwok and Morison [2015])
    mss = ATL07[beamStr+'/sea_ice_segments/geophysical/height_segment_mss'][:]
    
    # Photon rate of the given segment
    photon_rate = ATL07[beamStr+'/sea_ice_segments/stats/photon_rate'][:]
    
    # Estimated background rate from sun angle, reflectance, surface slope
    background_rate = ATL07[beamStr+'/sea_ice_segments/stats/backgr_calc'][:]
    
    ATL07.close()
    
    if numpy:
        # list the variables you want to output here..
        return along_track_dist, elev
    
    else:
        dF = pd.DataFrame({'elev':elev, 'lons':lons, 'lats':lats, 'ssh_flag':ssh_flag,
                          'quality_flag':quality,
                           'delta_time':delta_time,
                           'along_track_distance':along_track_distance,
                           'height_segment_id':height_segment_id, 
                           'photon_rate':photon_rate,'background_rate':background_rate,
                          'datetime':tiso, 'mss': mss, 'seg_length':seg_length})
        
         # Add the datetime string
        #dFtimepd=pd.to_datetime(dFtime)
        #dF['datetime'] = pd.Series(dFtimepd, index=dF.index)
        
        # Filter out high elevation values 
        dF = dF[(dF['elev']<maxElev)]
        # Reset row indexing
        dF=dF.reset_index(drop=True)
        return dF


def getATL10data(fileT, beam='gt1r', minFreeboard=0, maxFreeboard=10):
    """ Pandas/numpy ATL10 reader
    Written by Alek Petty, June 2018 (alek.a.petty@nasa.gov)

	I've picked out the variables from ATL10 I think are of most interest to sea ice users, 
    but by no means is this an exhastive list. 
    See the xarray or dictionary readers to load in the more complete ATL10 dataset
    or explore the hdf5 files themselves (I like using the app Panpoly for this) to see what else you might want
    
	Args:
		fileT (str): File path of the ATL10 dataset
		beamStr (str): ICESat-2 beam (the number is the pair, r=strong, l=weak)
        maxFreeboard (float): maximum freeboard (meters)

	returns:
        pandas dataframe
        
    Versions:
        v1: June 2018
        v2: June 2020 - cleaned things up, changed the time function slightly to be consistent with Ellen's ATL07 reader.

	"""

    print('ATL10 file:', fileT)
    
    f1 = h5py.File(fileT, 'r')
    
    # Freeboards
    freeboard=f1[beam]['freeboard_beam_segment']['beam_freeboard']['beam_fb_height'][:]
    ssh_flag=f1[beam]['freeboard_beam_segment']['height_segments']['height_segment_ssh_flag'][:]
    
    # ATL07 heights
    height=f1[beam]['freeboard_beam_segment']['height_segments']['height_segment_height'][:]
    
    # Freeboard confidence and freeboard quality flag
    freeboard_confidence=f1[beam]['freeboard_beam_segment']['beam_freeboard']['beam_fb_confidence'][:]
    freeboard_quality=f1[beam]['freeboard_beam_segment']['beam_freeboard']['beam_fb_quality_flag'][:]
    
    # Delta time in gps seconds
    delta_time = f1[beam]['freeboard_beam_segment']['beam_freeboard']['delta_time'][:]
    
    # Along track distance from the equator
    seg_x = f1[beam]['freeboard_beam_segment']['beam_freeboard']['seg_dist_x'][:]
    
    # Height segment ID (10 km segments)
    height_segment_id=f1[beam]['freeboard_beam_segment']['beam_freeboard']['height_segment_id'][:]
    
    lons=f1[beam]['freeboard_beam_segment']['beam_freeboard']['longitude'][:]
    lats=f1[beam]['freeboard_beam_segment']['beam_freeboard']['latitude'][:]
    
    # Time since the start of the granule
    deltaTimeRel=delta_time-delta_time[0]
    
    # #Add this value to delta time parameters to compute full gps_seconds
    atlas_epoch=f1['/ancillary_data/atlas_sdp_gps_epoch'][0] 
    gps_seconds = atlas_epoch + delta_time

    ## Use astropy to convert GPS time to UTC time
    tiso=Time(gps_seconds,format='gps').utc.datetime

    dF = pd.DataFrame({'freeboard':freeboard, 'freeboard_quality':freeboard_quality, 'height':height, 'ssh_flag':ssh_flag, 'lon':lons, 'lat':lats, 'delta_time':delta_time,'deltaTimeRel':deltaTimeRel, 
                     'height_segment_id':height_segment_id,'datetime': tiso, 'seg_x':seg_x})
    
    dF = dF[(dF['freeboard']>=minFreeboard)]
    dF = dF[(dF['freeboard']<=maxFreeboard)]
    
    # Also filter based on the confidence and/or quality flag?
    
    # Reset row indexing
    dF=dF.reset_index(drop=True)

    return dF