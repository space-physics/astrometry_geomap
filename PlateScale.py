#!/usr/bin/env python
"""
script to plate scale data in FITS or HDF5 format.

Michael Hirsch
"""
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
from argparse import ArgumentParser
import astrometry_azel.io as aio
import astrometry_azel as ael
import astrometry_azel.plots as aep
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('paper')


def doplatescale(infn: Path, outfn: Path,
                 latlon: Tuple[float, float],
                 ut1: Optional[datetime],
                 Navg: int,
                 solve: bool, args: str):

    # %% filenames
    infn = Path(infn).expanduser()

    if outfn:
        outfn = Path(outfn).expanduser()
    else:
        outfn = infn.with_suffix('.nc')
    fitsfn = outfn.with_suffix('.fits')
# %% convert to mean
    meanimg, ut1 = aio.meanstack(infn, Navg, ut1)

    aio.writefits(meanimg, fitsfn)
# %% try to get site coordinates from file
    if latlon is None:
        latlon = aio.readh5coord(infn)

    scale = ael.fits2azel(fitsfn, latlon, ut1, solve, args)
# %% plot
    aep.plotradec(scale)
    aep.plotazel(scale)
# %% write to file
    outfn = scale.filename.with_suffix('.nc')
    print('saving', outfn)
    scale.attrs['filename'] = str(scale.filename)
    try:
        scale.attrs['time'] = str(scale.time)
    except AttributeError:
        pass
    scale.to_netcdf(outfn)

    show()


def main():
    p = ArgumentParser(description='do plate scaling for image data')
    p.add_argument('infn', help='image data file name (HDF5 or FITS)')
    p.add_argument('-o', '--outfn', help='platescale data path to write')
    p.add_argument('-c', '--latlon', help='wgs84 coordinates of cameras (deg.)',
                   nargs=2, type=float)
    p.add_argument('-t', '--ut1', help='override file UT1 time yyyy-mm-ddTHH:MM:SSZ')
    p.add_argument('-N', '--navg', help='number of frames or start,stop frames to avg',
                   nargs='+', type=int, default=10)
    p.add_argument('-s', '--solve', help='run solve-field step of astrometry.net',
                   action="store_true")
    p.add_argument('-a', '--args', help='arguments to pass through to solve-field')
    P = p.parse_args()

    doplatescale(P.infn, P.outfn, P.latlon, P.ut1, P.navg, P.solve, P.args)


if __name__ == '__main__':
    main()
