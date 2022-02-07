import readers as rd
from .dataset import *

class ATL07(DataSet):

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
        
        return rd.getATL07(is2_f,beam)

    def visualize(self):
        print('visualization function has yet to be implemented')
        pass