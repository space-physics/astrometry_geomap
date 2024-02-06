#!/usr/bin/env python3
"""
Plot overlay of images that have been registered (RA/DEC is adequte).
For simplicity, the FITS images with Astrometry.net inserted WCS coordinates are used.

The program could be slightly upgraded to optionally use the original image and the .wcs file from Astrometry.net.

Note: one can use WCS projection:
http://docs.astropy.org/en/stable/visualization/wcsaxes/

Example

    python OverlayAltitudes.py blue.new red.new green.new
"""

from pathlib import Path
from argparse import ArgumentParser

from astropy.io import fits
from astropy.wcs import wcs
import numpy as np

from matplotlib.pyplot import figure, show
from matplotlib.colors import LogNorm


def main():
    p = ArgumentParser()
    p.add_argument("flist", help='FITS ".new" WCS registered filenames to plot together', nargs="+")
    p.add_argument("-s", "--subplots", help="subplots instead of overlay", action="store_true")
    p.add_argument("--suptitle", help="overall text for suptitle")
    p = p.parse_args()

    flist = [Path(f).expanduser() for f in p.flist]

    cmaps = ("Blues", "Reds", "Greens")
    fg = figure()
    fg.suptitle(p.suptitle)

    if p.subplots:
        axs = fg.subplots(1, len(flist), sharey=True, sharex=True)
        for fn, ax in zip(flist, axs):
            add_plot(fn, "gray", ax)

    else:
        ax = fg.gca()
        for fn, cm in zip(flist, cmaps):
            add_plot(fn, cm, ax, alpha=0.05)

    show()


def add_plot(fn: Path, cm, ax, alpha=1):
    """Astrometry.net makes file ".new" with the image and the WCS SIP 2-D polynomial fit coefficients in the FITS header

    We use DECL as "x" and RA as "y".
    pcolormesh() is used as it handles arbitrary pixel shapes.
    Note that pcolormesh() cannot tolerate NaN in X or Y (NaN in C is OK).
    This is handled in https://github.com/scivision/pcolormesh_nan.py.
    """

    with fits.open(fn, mode="readonly", memmap=False) as f:
        img = f[0].data

        yPix, xPix = f[0].shape[-2:]
        x, y = np.meshgrid(range(xPix), range(yPix))  # pixel indices to find RA/dec of
        xy = np.column_stack((x.ravel(order="C"), y.ravel(order="C")))

        radec = wcs.WCS(f[0].header).all_pix2world(xy, 0)

    ra = radec[:, 0].reshape((yPix, xPix), order="C")
    dec = radec[:, 1].reshape((yPix, xPix), order="C")

    ax.set_title(fn.name)
    ax.pcolormesh(ra, dec, img, alpha=alpha, cmap=cm, norm=LogNorm())
    ax.set_ylabel("Right Ascension [deg.]")
    ax.set_xlabel("Declination [deg.]")


if __name__ == "__main__":
    main()
