#!/usr/bin/env python3
"""
script to plate scale data in FITS or HDF5 format.

If the image starfile was solved using astrometry.net web service,
the ".new" FITS file is the input to this program.
"""

from pathlib import Path
from argparse import ArgumentParser

from astrometry_azel.project import plate_scale
import astrometry_azel.plot as plot


p = ArgumentParser(description="do plate scaling for image data")
p.add_argument("infn", help="image data file name (HDF5 or FITS)")
p.add_argument("latlon", help="wgs84 coordinates of cameras (deg.)", nargs=2, type=float)
p.add_argument("ut1", help="UT1 time yyyy-mm-ddTHH:MM:SSZ")
p.add_argument("-s", "--solve", help="run solve-field step of astrometry.net", action="store_true")
p.add_argument("-a", "--args", help="arguments to pass through to solve-field", default="")
P = p.parse_args()

path = Path(P.infn).expanduser()

print(P.latlon)

try:
    scale, img = plate_scale(path, P.latlon, P.ut1, P.solve, P.args)
except FileNotFoundError as e:
    if "could not find WCS file" in str(e):
        raise RuntimeError(
            f"Please specify PlateScale.py --solve option to run solve-field on {path}"
        )

outfn = Path(scale.filename)
outdir = outfn.parent
outstem = outfn.stem

fnr = outdir / (outstem + "_radec.png")
fna = outdir / (outstem + "_azel.png")

print("writing", fnr, fna)

fg = plot.ra_dec(scale, img=img)
fg.savefig(fnr)

fg = plot.az_el(scale, img=img)
fg.savefig(fna)
