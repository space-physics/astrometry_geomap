#!/usr/bin/env python3

"""
Overlay stars from a catalog on an image.
This is like a closed loop check that solve-field output (here, the .rdls file) makes sense.
"""

import argparse

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
ax.set_title(f"{p.rdls_file} stars on {p.new_file}", wrap=True)

ax.scatter(source_ra["ra"], source_ra["dec"], s=10, c="r", marker=".", label="stars")

show()
