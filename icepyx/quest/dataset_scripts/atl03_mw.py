from .dataset import *
from icepyx import Query
from os import mkdir
import h5py

class ATL03(DataSet):
    
'''We are having issues with this presently because the downloaded ATL03 data doesn't appear to have the same file structure as is assumed in the readers. This may be a version control issue? Might need to write out/find more readers based upon version (check if this is also the case for ATL07). Other issues: how to handle credentials in all of this, the download process is pretty slow and we need to create directories for it, seems like it might be difficult and not that user friendly at the moment to determine what you actually need or don't'''
    
    def __init__(self, boundingbox, timeframe):
        super().__init__(boundingbox, timeframe)
        self.df = self._read_in_dat()
    
    def _read_in_dat(self):
        
        dat = {} #initalize empty dictionary 
        short_name = 'ATL03'
        makedirs('../scripts/colocated/is2/' + shortname) # might need to create a directory for the data, 
        
        # how to handle credentialing? 
        earthdata_uid = 'mwiering' #self.ID?
        email = 'molly.m.wieringa@gmail.com' #self.email?
        
        data = Query(short_name, self.boundingbox, self.timeframe)
        data.avail_granules()
        
        data.earthdata_login(earthdata_uid, email)
        
        # do we actually want to download all the data every time?
        path = './colocated/is2/' + short_name
        data.download_granules(path)
        files = data.avail_granules(ids=True)
        
        for file in files:
            f = h5py.File(path+file, 'r')
            
            orientation  = is2_f['orbit_info/sc_orient'][0] # Check forward/backward orientation
            beam = None
            if orientation == 0:
                # take left beam if backward orientation
                beam = 'gt1l'
            elif orientation == 1:
                # take right beam if in forward orientation
                beam = 'gt1r'
            else:
                print('Error: Beam orientation unknown. Process terminated.')
                return 
             
            df = rd.getATL03(f,beam)
        
            #trim to bounding box
            df_cut=df[self.boundingbox]
        
            #convert time to UTC
            epoch=f['/ancillary_data/atlas_sdp_gps_epoch'][0]
            df_cut['time']=Time(epoch+df_cut['dt'],format='gps').utc.datetime
        
            #caculate along track distance
            df_cut['AT_dist']=df_cut.x-df_cut.x.values[0]
        
            #save a dictionary entry in the DataSet
            dat[file] = df_cut
        
        return dat
        
        
    def _add2plot(self, ax):
        pass

    def visualize(self):
        
        var= 'heights' #choose which variable we want to plot

        ## we will want to set colorbar parameters based on the chosen variable
        vmin=-10
        vmax=30
        ticks=np.arange(-20,100,5)

        # need to choose an appropriate projection
        proj = None
        min_lat = min(self.df['lats'])
        max_lat = max(self.df['lats'])
#         min_lon = min(self.df['lons'])
#         max_lon = max(self.df['lons'])
        if min_lat > 60:
            proj = ccrs.NorthPolarStereo(central_longitude=0.0, true_scale_latitude=None, globe=None)
        elif max_lat < -60:
            proj = ccrs.SouthPolarStereo(central_longitude=0.0, true_scale_latitude=None, globe=None)
        else:
            proj = ccrs.PlateCarree(central_longitude=0)
        

        # cartopy - need to make figure and set projection first before adding data
        plt.figure(figsize=(8,8), dpi= 90)
        ax = plt.axes(projection=proj) # choose polar sterographic for projection
        ax.coastlines(resolution='50m', color='black', linewidth=1)
        ax.set_extent(self.bounding_box, ccrs.PlateCarree())
        plt.scatter(self.df['lons'][::1000], self.df['lats'][::1000],c=self.df[var][::1000], cmap='viridis', \
                    vmin=vmin,vmax=vmax,transform=ccrs.PlateCarree())
        plt.colorbar(label=var, shrink=0.5, ticks=ticks,extend='both');