#!/usr/bin/env python
"""
script to plate scale data in FITS or HDF5 format.

Michael Hirsch
"""
from pathlib import Path
import h5py
import logging
#
from astrometry_azel.io import meanstack,writefits
from astrometry_azel import fits2azel

def doplatescale(infn:Path, outfn:Path, latlon:tuple, ut1, Navg, skipsolve:bool):
    infn = Path(infn).expanduser()

    if outfn:
        outfn = Path(outfn).expanduser()
    else:
        outfn = infn.with_suffix('.nc')

    fitsfn = outfn.with_suffix('.fits')
#%% convert to mean
    meanimg,ut1 = meanstack(infn,Navg,ut1)
    writefits(meanimg,fitsfn)
#%% try to get site coordinates from file
    if not latlon:
        if infn.suffix=='.h5':
            with h5py.File(infn, 'r') as f:
                try:
                    latlon = [f['/sensorloc']['glat'], f['/sensorloc']['glon']]
                except KeyError:
                    try:
                        latlon = f['/lla'][:2]
                    except KeyError as e:
                        logging.error(f'could not get camera coordinates from {infn}, will compute only RA/DEC  {e}')
        else:
            logging.error(f'could not get camera coordinates from {infn}, will compute only RA/DEC')
#%%
    return fits2azel(fitsfn,latlon, ut1, skipsolve)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='do plate scaling for image data')
    p.add_argument('infn',help='image data file name (HDF5 or FITS)')
    p.add_argument('-o','--outfn',help='platescale data path to write')
    p.add_argument('-c','--latlon',help='wgs84 coordinates of cameras (deg.)',nargs=2,type=float)
    p.add_argument('-t','--ut1',help='override file UT1 time yyyy-mm-ddTHH:MM:SSZ')
    p.add_argument('-N','--navg',help='number of frames or start,stop frames to avg',nargs='+',type=int,default=10)
    p.add_argument('-s','--skip',help='skip solve-field step of astrometry.net',action="store_true") #implies default False
    p = p.parse_args()


    scale = doplatescale(p.infn, p.outfn, p.latlon, p.ut1, p.navg, p.skip)
