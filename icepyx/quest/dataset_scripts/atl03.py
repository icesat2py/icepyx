from .dataset import *

class ATL03(DataSet):
    
    def __init__(self, boundingbox, timeframe):
        super().__init__(boundingbox, timeframe)
        self.df = self._read_in_dat()
    
    def _read_in_dat(self):
        
        temp_dloc = '/home/jovyan/'
        path  = 'shared/leading_to_phytoplankton/IS2_S2/ATL03_20190805215948_05930404_002_02.h5'
        
        is2_f = h5py.File(temp_dloc+path, 'r') # read hdf5 file
        orientation  = is2_f['orbit_info/sc_orient'][0] # Check forward/backward orientation
        beam = None
        if orientation == 0:
            # take left beam if backward orientation
            beam = 'gt1l'
        elif orientation == 1:
            # take righht beam if in forward orientation
            beam = 'gt1r'
        else:
            print('Error: Beam orientation unknown. Process terminated.')
            return
        
        return rd.getATL03(is2_f,beam)
        
        
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