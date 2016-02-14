#!/usr/bin/env python3
"""
Image stack -> average -> write FITS
Michael Hirsch

Because ImageJ has been a little buggy about writing FITS files, in particular the header
that astrometry.net then crashes on, we wrote this quick script to ingest a variety
of files and average the specified frames then write a FITS.
The reason we average a selected stack of images is to reduce the noise for use in
astrometry.net

The error you might get from an ImageJ saved FITS when reading in:
PyFits, AstroPy, or ImageMagick is:
IOError: Header missing END card.
"""
from pathlib import Path
from astropy.io import fits
from scipy.ndimage import imread
from scipy.io import loadmat
from skimage.color import rgb2gray
import h5py
import tifffile

def meanstack(infn,Navg,ut1=None):
    infn = Path(infn).expanduser()
#%% parse indicies to load
    if isinstance(Navg,int):
        key = range(0,Navg) #DO NOT use s_
    elif len(Navg) == 1:
        key = range(0,Navg[0]) #DO NOT use s_
    else:
        key = range(Navg[0],Navg[1]) #DO NOT use s_
#%% load images
    """
    some methods handled individually to improve efficiency with huge memory mapped files
    """
    if infn.suffix =='.h5':
        with h5py.File(str(infn),'r',libver='latest') as f:
            img = f['/rawimg']
            if len(img.shape)==2: #h5py has no .ndim like numpy
                meanimg = img.value
            elif len(img.shape)==3:
                meanimg = img[key,...].mean(axis=0).astype(img.dtype)

            if ut1 is None:
                try:
                    ut1 = f['/ut1_unix'][key[0]]
                except KeyError:
                    pass

        return meanimg,ut1

    elif infn.suffix == '.fits':
        with fits.open(str(infn),mode='readonly',memmap=False) as f: #mmap doesn't work with BZERO/BSCALE/BLANK
            img = f[0].data
    elif infn.suffix.startswith('.tif'):
        img = tifffile.imread(str(infn),key=key)
        if img.ndim==2:
            return img,ut1
        return img.mean(axis=0).astype(img.dtype)
    elif infn.suffix == '.mat':
        img = loadmat(str(infn))
        img = img['data'].T #matlab is fortran order
    else:
        img = imread(str(infn))
        if img.ndim==3 and img.shape[2]==3: #assume RGB
            img = rgb2gray(img)

    if img.ndim==2: #can't average just one image!
        return img,ut1
#%% return mean
    return img[key,...].mean(axis=0).astype(img.dtype),ut1  #assumes we iterate over first axis

def writefits(img,outfn):
    outfn = Path(outfn).expanduser()
    print('writing {}'.format(outfn))

    f = fits.PrimaryHDU(img)
    f.writeto(str(outfn),clobber=True,checksum=True)
    #no close

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='takes mean of first N images and writes new FITS file')
    p.add_argument('infn',help='FITS input file to read')
    p.add_argument('-N','--Navg',help='avg first N frames, or range(start,stop) of frame if two args given',nargs='+',default=(10,),type=int)
    p = p.parse_args()

    infn = Path(p.infn)

    meanimg = meanstack(infn,p.Navg)

    writefits(meanimg,infn.with_suffix('_mean.fits'))
