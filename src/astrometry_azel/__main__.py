#!/usr/bin/env python3
"""
script to plate scale data in FITS or HDF5 format.

If the image starfile was solved using astrometry.net web service,
the ".new" FITS file is the input to this program.
"""

from pathlib import Path
from argparse import ArgumentParser
import importlib.resources as ir

from astrometry_azel.project import plate_scale
import astrometry_azel.plot as plot


def main(path, latlon, ut1, solve, args, index_dir):
    try:
        scale, img = plate_scale(path, latlon, ut1, solve, args, index_dir=index_dir)
    except FileNotFoundError as e:
        if "could not find WCS file" in str(e):
            raise RuntimeError(
                f"Please specify --solve option to run solve-field on {path}"
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


if __name__ == "__main__":
    p = ArgumentParser(description="do plate scaling for image data")
    p.add_argument("infn", help="image data file name (HDF5 or FITS)")
    p.add_argument("latlon", help="wgs84 coordinates of cameras (deg.)", nargs=2, type=float)
    p.add_argument("ut1", help="UT1 time yyyy-mm-ddTHH:MM:SSZ")
    p.add_argument(
        "-i",
        "--index-dir",
        help="directory containing astrometry.net index files",
        default=ir.files(f"{__package__}") / "index_data",
    )
    p.add_argument("-s", "--solve", help="run solve-field step of astrometry.net", action="store_true")
    p.add_argument("-a", "--args", help="arguments to pass through to solve-field", default="")
    P = p.parse_args()

    path = Path(P.infn).expanduser()

    print(P.latlon)

    main(path, P.latlon, P.ut1, P.solve, P.args, index_dir=P.index_dir)
