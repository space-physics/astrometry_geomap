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

import typing
from pathlib import Path
from argparse import ArgumentParser

from astrometry_azel.plot import wcs_image

from matplotlib.pyplot import figure, show


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
    axs: typing.Any = fg.subplots(1, len(flist), sharey=True, sharex=True)
    for fn, ax in zip(flist, axs):
        wcs_image(fn, "gray", ax)

else:
    ax = fg.gca()
    for fn, cm in zip(flist, cmaps):
        wcs_image(fn, cm, ax, alpha=0.05)

show()
