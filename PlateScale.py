#!/usr/bin/env python3
"""
script to plate scale data in FITS or HDF5 format.

If the image starfile was solved using astrometry.net web service,
the ".new" FITS file is the input to this program.
"""

from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

import astrometry_azel.io as aio
import astrometry_azel as ael

try:
    import astrometry_azel.plots as aep
except ImportError as err:
    print(f"plotting skipped: {err}", file=sys.stderr)
    aep = None  # type: ignore


def doplatescale(
    file: Path,
    latlon: tuple[float, float],
    ut1: datetime | None,
    Navg: int,
    solve: bool,
    args: str,
) -> tuple:
    # %% filenames
    infn = Path(file).expanduser().resolve()

    # %% get mean of image stack to improve image SNR
    meanimg, ut1 = aio.meanstack(infn, Navg, ut1)

    if solve:
        aio.writefits(meanimg, file.with_stem(file.stem + "_stack"))
    # %% try to get site coordinates from file
    if latlon is None:
        if infn.suffix == ".h5":
            latlon = aio.readh5coord(infn)
        else:
            raise ValueError("please specify camera lat,lon on command line")

    scale = ael.fits2azel(file, latlon=latlon, time=ut1, solve=solve, args=args)

    # %% write to file
    outfn = Path(scale.filename).with_suffix(".nc")
    print("saving", outfn)
    try:
        scale.attrs["time"] = str(scale.time)
    except AttributeError:
        pass
    scale.to_netcdf(outfn)

    return scale, meanimg


def convert(
    infn: Path,
    ut1: datetime,
    Navg: int,
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
    scale, img = doplatescale(infn, latlon, ut1, Navg, solve, args)

    outfn = Path(scale.filename)
    outdir = outfn.parent
    outstem = outfn.stem

    if aep is not None:
        fnr = outdir / (outstem + "_radec.png")
        fna = outdir / (outstem + "_azel.png")
        print("writing", fnr, fna)
        fg = aep.plotradec(scale, img=img)
        fg.savefig(fnr)
        fg = aep.plotazel(scale, img=img)
        if fg is not None:
            fg.savefig(fna)
        else:
            print("input time and coordinates to make azimuth, elevation plots", file=sys.stderr)

    return outfn


def main():
    p = ArgumentParser(description="do plate scaling for image data")
    p.add_argument("infn", help="image data file name (HDF5 or FITS)")
    p.add_argument(
        "-c", "--latlon", help="wgs84 coordinates of cameras (deg.)", nargs=2, type=float
    )
    p.add_argument(
        "-t", "--ut1", help="override file UT1 time yyyy-mm-ddTHH:MM:SSZ or (start, stop)"
    )
    p.add_argument(
        "-N",
        "--navg",
        help="number of frames or start,stop frames to avg",
        nargs="+",
        type=int,
        default=10,
    )
    p.add_argument(
        "-s", "--solve", help="run solve-field step of astrometry.net", action="store_true"
    )
    p.add_argument("-a", "--args", help="arguments to pass through to solve-field", default="")
    P = p.parse_args()

    path = Path(P.infn).expanduser()

    print(P.latlon)

    convert(path, P.ut1, P.navg, P.solve, P.latlon, P.args)


if __name__ == "__main__":
    main()
