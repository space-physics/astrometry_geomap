#!/usr/bin/env python3
"""
script to plate scale data in FITS or HDF5 format.

Michael Hirsch
"""
import h5py
from pathlib import Path
from tempfile import mkstemp
from warnings import warn
#
from astrometry_azel.imgAvgStack import meanstack,writefits
from astrometry_azel.fits2azel import fits2azel

def doplatescale(infn,outfn,latlon,ut1):
    infn = Path(infn).expanduser()
    outfn = Path(outfn).expanduser()
    fitsfn = outfn.with_suffix('.fits')
#%% convert to mean
    meanimg,ut1 = meanstack(infn,1,ut1)
    writefits(meanimg,fitsfn)
#%% try to get site coordinates from file
    if not latlon:
        with h5py.File(str(infn),'r',libver='latest') as f:
            try:
                latlon = [f['/sensorloc']['glat'], f['/sensorloc']['glon']]
            except KeyError:
                try:
                    latlon = f['/lla'][:2]
                except KeyError as e:
                    warn('could not get camera coordinates from {}, will compute only RA/DEC  {}'.format(infn,e))
#%%
    x,y,ra,dec,az,el,timeFrame = fits2azel(fitsfn,latlon,ut1,['show','h5','png'],(0,2800))

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='do plate scaling for image data')
    p.add_argument('infn',help='image data file name (HDF5 or FITS)')
    p.add_argument('-o','--outfn',help='platescale data file name to write',default=mkstemp('.h5')[1])
    p.add_argument('--latlon',help='wgs84 coordinates of cameras (deg.)',nargs=2,type=float)
    p.add_argument('--ut1',help='override file UT1 time yyyy-mm-ddTHH:MM:SSZ')
    p = p.parse_args()

    doplatescale(p.infn,p.outfn,p.latlon,p.ut1)
