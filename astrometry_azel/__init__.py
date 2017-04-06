from pathlib import Path
import subprocess
import h5py
from numpy import meshgrid,column_stack
from astropy.wcs import wcs
import logging
from astropy.io import fits #instead of obsolete pyfits
from dateutil.parser import parse
from datetime import datetime
from pytz import UTC
#
from pymap3d import radec2azel
#
from .plots import plotazel,plotradec
#%%

def readfitsimagestack(fn):
    fn = Path(fn).expanduser()

    with fits.open(fn, mode='readonly') as f:
        if len(f[0].shape) > 1: #no .ndim in Astropy.io.fits 1.2
            return f[0].data
        else:
            raise TypeError(f'did not find image data in {fn}. This may be a bug.')


def fits2radec(fitsfn,camLatLon,makeplot,clim=None):
    fitsfn = Path(fitsfn).expanduser()

    if fitsfn.suffix == '.fits':
        WCSfn = fitsfn.with_suffix('.wcs') #using .wcs will also work but gives a spurious warning

    elif fitsfn.suffix == '.wcs':
        makeplot.append('skipsolve')
        WCSfn = fitsfn
    else:
        raise TypeError(f'please convert {fitsfn} to GRAYSCALE .fits e.g. with ImageJ or ImageMagick')

    if not 'skipsolve' in makeplot:
        doSolve(fitsfn)

    with fits.open(fitsfn, mode='readonly') as f:
        yPix,xPix = f[0].shape[-2:]

    x,y = meshgrid(range(xPix), range(yPix)) #pixel indices to find RA/dec of
    xy = column_stack((x.ravel(order='C'), y.ravel(order='C')))
#%% use astropy.wcs to register pixels to RA/DEC
    """
    http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html#astropy.wcs.WCS
    naxis=[0,1] is to take x,y axes in case a color photo was input e.g. to astrometry.net cloud solver
    """
    try:
        with fits.open(WCSfn, mode='readonly') as f:
            #radec = wcs.WCS(hdul[0].header,naxis=[0,1]).all_pix2world(xy, 0)
            radec = wcs.WCS(f[0].header).all_pix2world(xy, 0)
    except IOError:
        raise RuntimeError(f'It appears the WCS solution is not present, was the FITS image solved?  looking for: {WCSfn}')

    ra  = radec[:,0].reshape((yPix,xPix),order='C')
    dec = radec[:,1].reshape((yPix,xPix),order='C')
#%% plot
    plotradec(ra,dec,x,y,camLatLon,fitsfn,makeplot)

    return x,y,ra,dec


def r2ae(fitsFN,ra,dec,x,y,camLatLon,specTime,makeplot):
    if camLatLon is not None and ra is not None:
        try:
            if specTime is None:
                with fits.open(fitsFN,mode='readonly') as f:
                    frameTime = f[0].header['FRAME'] #TODO this only works from Solis?
                    timeFrame = parse(frameTime).replace(tzinfo=UTC)
                    logging.warning('assumed UTC time zone, using FITS header for time')
            elif isinstance(specTime,datetime):
                timeFrame = specTime
            elif isinstance(specTime,(float,int)): #assume UT1_Unix
                timeFrame = datetime.fromtimestamp(specTime,tz=UTC)
            else: #user override of frame time
                timeFrame = parse(specTime)
        except (KeyError, TypeError):
            logging.error(f'could not read time from {fitsFN}')
            return (None,)*3
    else:
        return (None,)*3

    print(f'image time: {timeFrame}')

#%% knowing camera location, time, and sky coordinates observed, convert to az/el for each pixel
    az,el = radec2azel(ra, dec, camLatLon[0], camLatLon[1],timeFrame)

    plotazel(az,el,x,y,fitsFN,camLatLon,timeFrame,makeplot)

    return az,el,timeFrame


def doSolve(fitsfn):
    """
    Astrometry.net from at least version 0.67 is OK with Python 3.
    """
    #binpath = Path(find_executable('solve-field')).parent

    cmd = ['solve-field','--overwrite', str(fitsfn)]
    print(cmd)

    subprocess.run(cmd)#, env={'PATH':str(binpath)})

    print('\n\n *** done with astrometry.net ***\n ')


def fits2azel(fitsfn,camLatLon,specTime,makeplot, clim=None):
    fitsfn = Path(fitsfn).expanduser()

    x,y,ra,dec = fits2radec(fitsfn,camLatLon,makeplot, clim)
    az,el,timeFrame = r2ae(fitsfn,ra,dec,x,y,camLatLon,specTime, makeplot)

    if 'h5' in makeplot:
        h5fn = fitsfn.with_suffix('.h5')
        print(f'saving {h5fn}')
        writeh5(h5fn,az,el,camLatLon,x,y,ra,dec,timeFrame,fitsfn)

    return x,y,ra,dec,az,el,timeFrame


def writeh5(h5fn,az,el,camLatLon,x,y,ra,dec,timeFrame,fitsfn):
    with h5py.File(h5fn, 'w',libver='latest') as f:

        if az is not None:
            h5az = f.create_dataset("/az",data=az,compression="gzip",shuffle=True,fletcher32=True)
            h5az.attrs['Units'] = 'degrees'

            h5el = f.create_dataset("/el",data=el,compression="gzip",shuffle=True,fletcher32=True)
            h5el.attrs['Units'] = 'degrees'

            h5ll = f.create_dataset("/sensorloc",data=camLatLon,shuffle=True,fletcher32=True)
            h5ll.attrs['Units'] = 'WGS-84 degrees'

        h5x =  f.create_dataset("/x",data=x,compression="gzip",shuffle=True,fletcher32=True)
        h5x.attrs['Units'] = 'pixels'

        h5y =  f.create_dataset("/y",data=y,compression="gzip",shuffle=True,fletcher32=True)
        h5y.attrs['Units'] = 'pixels'

        h5ra = f.create_dataset("/ra",data=ra,compression="gzip",shuffle=True,fletcher32=True)
        h5ra.attrs['Units'] = 'degrees'

        h5dec =f.create_dataset("/dec",data=dec,compression="gzip",shuffle=True,fletcher32=True)
        h5dec.attrs['Units'] = 'degrees'

        h5tf = f.create_dataset("/timeFrame",data=str(timeFrame))
        h5tf.attrs['Units'] = 'UTC time of exposure start'

        h5fn = f.create_dataset('/fitsfn',data=str(fitsfn))
        h5fn.attrs['Units'] = 'original FITS filename'
