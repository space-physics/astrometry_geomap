#!/usr/bin/env python
"""
script to plate scale data in FITS or HDF5 format.

If you already solved the image using astrometry.net web service, the .new FITS file
is the input to this program.

Michael Hirsch
"""

from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
from argparse import ArgumentParser

import astrometry_azel.io as aio
import astrometry_azel as ael
from astrometry_azel.utils import datetime_range

try:
    import astrometry_azel.plots as aep
except ImportError as err:
    print(f"plotting skipped: {err}", file=sys.stderr)
    aep = None  # type: ignore
try:
    import seaborn as sns

    sns.set_context("paper")
except ImportError:
    pass


def doplatescale(
    infn: Path,
    outfn: Path,
    latlon: tuple[float, float],
    ut1: datetime | None,
    Navg: int,
    solve: bool,
    args: str,
) -> tuple:
    # %% filenames
    infn = Path(infn).expanduser().resolve(strict=True)
    wcsfn = infn.with_suffix(".wcs")

    if outfn:
        fitsfn = Path(outfn).with_suffix(".fits")
    else:
        fitsfn = infn.parent / (infn.stem + "_stack.fits")
    # %% convert to mean
    meanimg, ut1 = aio.meanstack(infn, Navg, ut1)

    aio.writefits(meanimg, fitsfn)
    # %% try to get site coordinates from file
    if latlon is None:
        latlon = aio.readh5coord(infn)

    scale = ael.fits2azel(fitsfn, wcsfn=wcsfn, latlon=latlon, time=ut1, solve=solve, args=args)
    if scale is None:
        return (None, None)
    # %% write to file
    if outfn:
        outfn = Path(outfn).expanduser()
    else:
        outfn = Path(scale.filename).with_suffix(".nc")
    print("saving", outfn)
    try:
        scale.attrs["time"] = str(scale.time)
    except AttributeError:
        pass
    scale.to_netcdf(outfn)

    return scale, meanimg


def convert(infn: Path, ut1: datetime, P) -> Path | None:
    scale, img = doplatescale(infn, P.outfn, P.latlon, ut1, P.navg, P.solve, P.args)
    if scale is None:
        return None

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
    p.add_argument("-g", "--glob", help="filename globbing")
    p.add_argument("-o", "--outfn", help="platescale data path to write")
    p.add_argument(
        "-c", "--latlon", help="wgs84 coordinates of cameras (deg.)", nargs=2, type=float
    )
    p.add_argument(
        "-t",
        "--ut1",
        help="override file UT1 time yyyy-mm-ddTHH:MM:SSZ or (start, stop)",
        nargs="+",
        default=[None],
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
    p.add_argument("-a", "--args", help="arguments to pass through to solve-field")
    P = p.parse_args()

    path = Path(P.infn).expanduser()

    if P.glob:
        start = parse(P.ut1[0])
        end = parse(P.ut1[1])
        files = list(path.glob(P.glob))
        total = len(files)
        ok = []
        if total == 0:
            raise FileNotFoundError(f"No files found in {path} with {P.glob}")
        step = (end - start) / len(files)
        times = datetime_range(start, end, step)
        for file, time in zip(files, times):
            converted = convert(file, time, P)
            if converted:
                ok.append(converted)
        print("converted", len(ok), "/", total, "files in", path)
    else:
        convert(path, P.ut1[0], P)


if __name__ == "__main__":
    main()
