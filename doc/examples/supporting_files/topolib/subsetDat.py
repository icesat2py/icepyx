import rasterio as rio
from pyproj import Proj, transform
import xarray as xr
import h5py

def subsetBBox(rast,proj_in,proj_out):

    # rasterio open data
    rB = rio.open(rast)
    # rasterio get bounding box
    [L,B,R,T] = rB.bounds

    if proj_in == proj_out:
        return L, R, T, B
    else:
        incord = Proj(init=proj_in)
        outcord = Proj(init=proj_out)

        [Left,Bottom] = transform(incord,outcord,L,B)
        [Right,Top] = transform(incord,outcord,R,T)
        return Left, Bottom, Right, Top

def subSetDatQual(dFrame,dat_met,upper,lower=None):
    
    initLen = len(dFrame[dat_met])
    
    if lower == None:
        dFrame = dFrame[dFrame[dat_met]==upper]
    else:
        dFrame = dFrame[dFrame[dat_met] > lower]
        dFrame = dFrame[dFrame[dat_met] < upper]
        
    endLen = len(dFrame[dat_met])
        
    print(f"filtered {initLen-endLen} points out of {initLen} ({round(100*endLen/initLen)}%)")
     
    return dFrame