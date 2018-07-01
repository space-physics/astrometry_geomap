#!/usr/bin/env python
"""
original frontend to fits2azel (requires fits input)
Consider using the more general PlateScale.py
"""
from matplotlib.pyplot import show
from argparse import ArgumentParser
from astrometry_azel import fits2azel
from astrometry_azel.plots import plotradec, plotazel


def main():
    p = ArgumentParser(description='converts fits starfield image to RA/Dec and az/el')
    p.add_argument('infile', help='.fits or .wcs filename with path', type=str)
    p.add_argument('-c', '--latlon', help='tuple of WGS-84 (lat,lon) [degrees]', nargs=2, type=float)
    p.add_argument('-t', '--time', help='override image time with UTC time yyyy-mm-ddThh:mm:ss')
    p.add_argument('-s', '--skip', help='skip solve-field step of astrometry.net', action="store_true")  # implies default False
    p.add_argument('--h5', help='write variables to .h5 HDF5 data file', action="store_true")
    p.add_argument('--clim', help='clim of preview images (no effect on computation)', nargs=2, default=None, type=float)
    P = p.parse_args()

# %% actually run program
    scale = fits2azel(P.infile, P.latlon, P.time, P.skip)

    plotradec(scale)
    plotazel(scale)

    if P.h5:
        outfn = scale.filename.with_suffix('.nc')
        print('saving', outfn)
        scale.attrs['filename'] = str(scale.filename)
        scale.attrs['time'] = str(scale.time)
        scale.to_netcdf(outfn)

    show()


if __name__ == "__main__":
    main()
