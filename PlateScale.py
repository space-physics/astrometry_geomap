#!/usr/bin/env python3
"""
script to plate scale data in FITS or HDF5 format.

If the image starfile was solved using astrometry.net web service,
the ".new" FITS file is the input to this program.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

import astrometry_azel.io as aio
import astrometry_azel as ael

import astrometry_azel.plot as plot


def doplatescale(
    in_file: Path,
    latlon: tuple[float, float],
    ut1: datetime,
    solve: bool,
    args: str,
) -> tuple:
    # %% filenames
    in_file = Path(in_file).expanduser().resolve()

    # %% convert input image to FITS
    new_file = in_file.parent / (in_file.stem + "_new.fits")
    img = aio.load_image(in_file)
    aio.write_fits(img, new_file)

    scale = ael.fits2azel(new_file, latlon=latlon, time=ut1, solve=solve, args=args)

    # %% write to file
    netcdf_file = Path(scale.filename).with_suffix(".nc")
    print("saving", netcdf_file)
    aio.write_netcdf(scale, netcdf_file)

    return scale, img


def convert(
    infn: Path,
    ut1: datetime,
    solve: bool,
    latlon: tuple[float, float],
    args: str = "",
) -> Path:
    """
    Obtain plate scale data from image file and write to netCDF file.

    Parameters
    ----------

    infn: pathlib.Path
        input file name
    ut1: datetime.datetime
        UT1 time of image
    P: argparse.Namespace
        command line arguments
    """

    scale, img = doplatescale(infn, latlon, ut1, solve, args)

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

    return outfn


p = ArgumentParser(description="do plate scaling for image data")
p.add_argument("infn", help="image data file name (HDF5 or FITS)")
p.add_argument("-c", "--latlon", help="wgs84 coordinates of cameras (deg.)", nargs=2, type=float)
p.add_argument("-t", "--ut1", help="override file UT1 time yyyy-mm-ddTHH:MM:SSZ or (start, stop)")
p.add_argument("-s", "--solve", help="run solve-field step of astrometry.net", action="store_true")
p.add_argument("-a", "--args", help="arguments to pass through to solve-field", default="")
P = p.parse_args()

path = Path(P.infn).expanduser()

print(P.latlon)

convert(path, P.ut1, P.solve, P.latlon, P.args)
