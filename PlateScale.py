#!/usr/bin/env python
"""
script to plate scale data in FITS or HDF5 format.

If you already solved the image using astrometry.net web service, the .new FITS file
is the input to this program.

Michael Hirsch
"""
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
from argparse import ArgumentParser
import xarray
import numpy as np

import astrometry_azel.io as aio
import astrometry_azel as ael

try:
    import astrometry_azel.plots as aep
    from matplotlib.pyplot import show
except (ImportError, RuntimeError):
    show = None
try:
    import seaborn as sns

    sns.set_context("paper")
except ImportError:
    pass


def doplatescale(
    infn: Path,
    outfn: Path,
    latlon: Tuple[float, float],
    ut1: Optional[datetime],
    Navg: int,
    solve: bool,
    args: str,
) -> Tuple[xarray.Dataset, np.ndarray]:

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

    scale = ael.fits2azel(
        fitsfn, wcsfn=wcsfn, latlon=latlon, time=ut1, solve=solve, args=args
    )
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


def main():
    p = ArgumentParser(description="do plate scaling for image data")
    p.add_argument("infn", help="image data file name (HDF5 or FITS)")
    p.add_argument("-o", "--outfn", help="platescale data path to write")
    p.add_argument(
        "-c",
        "--latlon",
        help="wgs84 coordinates of cameras (deg.)",
        nargs=2,
        type=float,
    )
    p.add_argument("-t", "--ut1", help="override file UT1 time yyyy-mm-ddTHH:MM:SSZ")
    p.add_argument(
        "-N",
        "--navg",
        help="number of frames or start,stop frames to avg",
        nargs="+",
        type=int,
        default=10,
    )
    p.add_argument(
        "-s",
        "--solve",
        help="run solve-field step of astrometry.net",
        action="store_true",
    )
    p.add_argument("-a", "--args", help="arguments to pass through to solve-field")
    P = p.parse_args()

    scale, img = doplatescale(P.infn, P.outfn, P.latlon, P.ut1, P.navg, P.solve, P.args)

    outfn = Path(scale.filename)
    outdir = outfn.parent
    outstem = outfn.stem

    if show is not None:
        aep.plotradec(scale, img=img).savefig(outdir / (outstem + "_radec.png"))
        aep.plotazel(scale, img=img).savefig(outdir / (outstem + "_azel.png"))

        show()


if __name__ == "__main__":
    main()
