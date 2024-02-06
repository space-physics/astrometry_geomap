#!/usr/bin/env python3

"""
Overlay stars from a catalog on an image.
This is like a closed loop check that solve-field output (here, the .rdls file) makes sense.

Use --tag-all option of solve-field to output star magnitude in the .rdls file:

    solve-field src/astrometry_azel/tests/apod4.fits --tag-all
"""

import argparse
from pathlib import Path

import numpy as np

from astrometry_azel.io import get_sources
from astrometry_azel.plot import wcs_image, xy_image

from matplotlib.pyplot import figure, show


def label_stars(ax, x, y, mag_norm=None):
    if mag_norm is not None:
        ax.scatter(
            x,
            y,
            s=100 * mag_norm,
            edgecolors="red",
            marker="o",
            facecolors="none",
            label="stars",
        )
    else:
        ax.scatter(
            x,
            y,
            s=25,
            edgecolors="red",
            marker="o",
            facecolors="none",
            label="stars",
        )


p = argparse.ArgumentParser()
p.add_argument(
    "stem", help="FITS file stem (without .suffix) output from solve-field (Astrometry.net)"
)
p = p.parse_args()

stem = Path(p.stem)
new = stem.with_suffix(".new")

rdls = stem.with_suffix(".rdls")
source_ra = get_sources(rdls)


xyls = stem.parent / (stem.name + "-indx.xyls")
source_xy = get_sources(xyls)

if "MAG" in source_ra.columns.names:
    Ntot = source_ra.shape[0]
    Nkeep = 20  # only plot the brightest stars

    i = source_ra.argsort(axis=0, order="MAG")

    source_ra = np.take_along_axis(source_ra, i, axis=0)[:Nkeep]
    source_xy = np.take_along_axis(source_xy, i, axis=0)[:Nkeep]

    # normalize star magnitude to [0,1]
    mag_norm = (source_ra["MAG"] - source_ra["MAG"].min()) / np.ptp(source_ra["MAG"])
    ttxt = f"{stem}: {source_ra.shape[0]} / {Ntot} stars"
else:
    mag_norm = None
    ttxt = f"{stem} {source_ra.shape[0]} stars"

# %% unwarped image

fgy = figure()
axy = fgy.gca()
xy_image(new, "gray", axy)

label_stars(axy, source_xy["X"], source_xy["Y"], mag_norm)
axy.set_title(ttxt, wrap=True)

# %% WCS warped image

fgr = figure()
axr = fgr.gca()
wcs_image(new, "gray", axr)

label_stars(axr, source_ra["RA"], source_ra["DEC"], mag_norm)
axr.set_title(ttxt, wrap=True)

show()
