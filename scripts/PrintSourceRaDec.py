#!/usr/bin/env python3
"""
Utility program to print source Coordinates in RA,DEC that astrometry.net found
use this with .rdls (rdls.fits) FITS files after solving an image
"""

import argparse

from astrometry_azel.io import get_sources


p = argparse.ArgumentParser(description="show RA DEC in .rdls files after solving an image")
p.add_argument("fn", help=".rdls file from astrometry.net")
p = p.parse_args()

radec_sources = get_sources(p.fn)

print(radec_sources.shape[0], "sources found in", p.fn, "with ra,dec coordinates:")

print(radec_sources)
