#!/usr/bin/env python3

"""
Overlay stars from a catalog on an image.
This is like a closed loop check that solve-field output (here, the .rdls file) makes sense.

Use --tag-all option of solve-field to output star magnitude in the .rdls file:

    solve-field src/astrometry_azel/tests/apod4.fits --tag-all
"""

import argparse

import numpy as np

from astrometry_azel.io import get_sources
from astrometry_azel.plot import add_image

from matplotlib.pyplot import figure, show


p = argparse.ArgumentParser()
p.add_argument("rdls_file", help="FITS .rdls filename output from solve-field (Astrometry.net)")
p.add_argument("new_file", help="FITS .new filename output from solve-field (Astrometry.net)")
p = p.parse_args()

source_ra = get_sources(p.rdls_file)

fg = figure()
ax = fg.gca()
add_image(p.new_file, "gray", ax)

if "MAG" in source_ra.columns.names:
    Ntot = source_ra.shape[0]
    Nkeep = 20  # only plot the brightest stars
    source_ra.sort(axis=0, order="MAG")
    source_ra = source_ra[:Nkeep]

    # normalize star magnitude to [0,1]
    mag_norm = (source_ra["MAG"] - source_ra["MAG"].min()) / np.ptp(source_ra["MAG"])

    ax.scatter(
        source_ra["RA"],
        source_ra["DEC"],
        s=100 * mag_norm,
        edgecolors="red",
        marker="o",
        facecolors="none",
        label="stars",
    )
    ttxt = f"{p.rdls_file} {source_ra.shape[0]} / {Ntot} stars on {p.new_file}"
else:
    ax.scatter(
        source_ra["RA"],
        source_ra["DEC"],
        s=25,
        edgecolors="red",
        marker="o",
        facecolors="none",
        label="stars",
    )
    ttxt = f"{p.rdls_file} {source_ra.shape[0]} stars on {p.new_file}"


ax.set_title(ttxt, wrap=True)

show()
