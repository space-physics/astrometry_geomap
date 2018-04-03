from pathlib import Path
import subprocess
from numpy import meshgrid,column_stack
from astropy.wcs import wcs
import logging
import xarray
from astropy.io import fits #instead of obsolete pyfits
from dateutil.parser import parse
from datetime import datetime
from pytz import UTC
#
from pymap3d import radec2azel


def fits2radec(fitsfn:Path, skipsolve:bool=False) -> xarray.Dataset:
    fitsfn = Path(fitsfn).expanduser()

    if fitsfn.suffix == '.fits':
        WCSfn = fitsfn.with_suffix('.wcs') #using .wcs will also work but gives a spurious warning

    elif fitsfn.suffix == '.wcs':
        WCSfn = fitsfn
    else:
        raise ValueError(f'please convert {fitsfn} to GRAYSCALE .fits e.g. with ImageJ or ImageMagick')

    if not skipsolve:
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
# %% collect output
    radec = xarray.Dataset({'ra': (('y','x'),ra),
                            'dec':(('y','x'),dec),},
                           {'x':range(xPix), 'y':range(yPix)},
                           attrs={'filename':fitsfn})

    return radec


def r2ae(scale:xarray.Dataset, camLatLon:tuple, time:datetime) -> xarray.Dataset:
    if camLatLon is not None and scale is not None:
        if time is None:
            with fits.open(scale.filename,mode='readonly') as f:
                time = f[0].header['FRAME'] #TODO this only works from Solis?
                time = parse(time).replace(tzinfo=UTC)
                logging.warning('assumed UTC time zone, using FITS header for time')
        elif isinstance(time,datetime):
            pass
        elif isinstance(time,(float,int)): #assume UT1_Unix
            time = datetime.fromtimestamp(time, tz=UTC)
        else: #user override of frame time
            time = parse(time)

    else:
        return (None,)*3

    print('image time:',time)
#%% knowing camera location, time, and sky coordinates observed, convert to az/el for each pixel
    az,el = radec2azel(scale['ra'], scale['dec'], camLatLon[0], camLatLon[1], time)
# %% collect output
    scale['az'] = (('y','x'),az)
    scale['el'] = (('y','x'),el)
    scale.attrs['lat'] = camLatLon[0]
    scale.attrs['lon'] = camLatLon[1]
    scale.attrs['time'] = time

    return scale


def doSolve(fitsfn):
    """
    Astrometry.net from at least version 0.67 is OK with Python 3.
    """
    #binpath = Path(find_executable('solve-field')).parent

    cmd = ['solve-field','--overwrite', str(fitsfn)]
    print(cmd)

    subprocess.check_call(cmd)

    print('\n\n *** done with astrometry.net ***\n ')


def fits2azel(fitsfn:Path, camLatLon:tuple, time:datetime, skipsolve:bool=False) -> xarray.Dataset:
    fitsfn = Path(fitsfn).expanduser()

    radec = fits2radec(fitsfn, skipsolve)
    scale = r2ae(radec, camLatLon, time)

    return scale
