from __future__ import annotations
from pathlib import Path
import subprocess
import shutil
import logging
import warnings
from dateutil.parser import parse
from datetime import datetime
from numpy import meshgrid, column_stack
import xarray
from astropy.io import fits  # instead of obsolete pyfits
from astropy.wcs import wcs

try:
    import pymap3d
except ImportError:
    pymap3d = None


def fits2radec(
    fitsfn: Path, WCSfn: Path = None, solve: bool = False, args: str = None
) -> xarray.Dataset:

    fitsfn = Path(fitsfn).expanduser()

    if WCSfn is None:
        if fitsfn.suffix in (".fits", ".new"):
            # using .wcs will also work but gives a spurious warning
            WCSfn = fitsfn.with_suffix(".wcs")
        elif fitsfn.suffix == ".wcs":
            WCSfn = fitsfn
        else:
            raise ValueError(f"please convert {fitsfn} to GRAYSCALE .fits")

    if solve:
        if not doSolve(fitsfn, args):
            logging.error(f"{fitsfn} was not solved")
            return None

    if not WCSfn.is_file():
        WCSfn = WCSfn.parent / (WCSfn.stem + "_stack.wcs")
    if not WCSfn.is_file():
        logging.error(f"it appears {fitsfn} was not solved as {WCSfn} is not found")
        return None

    with fits.open(fitsfn, mode="readonly") as f:
        yPix, xPix = f[0].shape[-2:]

    x, y = meshgrid(range(xPix), range(yPix))  # pixel indices to find RA/dec of
    xy = column_stack((x.ravel(order="C"), y.ravel(order="C")))
    # %% use astropy.wcs to register pixels to RA/DEC
    """
    http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html#astropy.wcs.WCS
    naxis=[0,1] is to take x,y axes in case a color photo was input e.g. to astrometry.net cloud solver
    """
    with fits.open(WCSfn, mode="readonly") as f:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            radec = wcs.WCS(f[0].header).all_pix2world(xy, 0)
            # radec = wcs.WCS(hdul[0].header,naxis=[0,1]).all_pix2world(xy, 0)

    ra = radec[:, 0].reshape((yPix, xPix), order="C")
    dec = radec[:, 1].reshape((yPix, xPix), order="C")
    # %% collect output
    radec = xarray.Dataset(
        {"ra": (("y", "x"), ra), "dec": (("y", "x"), dec)},
        {"x": range(xPix), "y": range(yPix)},
        attrs={"filename": str(fitsfn)},
    )

    return radec


def radec2azel(
    scale: xarray.Dataset, latlon: tuple[float, float], time: datetime
) -> xarray.Dataset:

    if pymap3d is None:
        logging.error("azimuth, elevation computations require: pip install pymap3d")
        return None
    if latlon is None:
        return None
    if not isinstance(scale, xarray.Dataset):
        return None

    if time is None:
        with fits.open(scale.filename, mode="readonly") as f:
            try:
                t = f[0].header["FRAME"]  # TODO this only works from Solis?
            except KeyError:
                return None
        time = parse(t)
        logging.info("using FITS header for time")
    elif isinstance(time, datetime):
        pass
    elif isinstance(time, (float, int)):  # assume UT1_Unix
        time = datetime.utcfromtimestamp(time)
    else:  # user override of frame time
        time = parse(time)

    print("image time:", time)
    # %% knowing camera location, time, and sky coordinates observed, convert to az/el for each pixel
    # .values is to avoid silently freezing AstroPy
    az, el = pymap3d.radec2azel(scale["ra"].values, scale["dec"].values, *latlon, time)
    if (el < 0).any():
        Nbelow = (el < 0).nonzero()
        logging.error(
            f"{Nbelow} points were below the horizon."
            "Currently this program assumed observer ~ ground level."
            "Please file a bug report if you need observer off of Earth surface"
        )
    # %% collect output
    scale["az"] = (("y", "x"), az)
    scale["el"] = (("y", "x"), el)
    scale.attrs["lat"] = latlon[0]
    scale.attrs["lon"] = latlon[1]
    scale.attrs["time"] = time
    return scale


def doSolve(fitsfn: Path, args: str = None) -> bool:
    """
    Astrometry.net from at least version 0.67 is OK with Python 3.
    """
    solve = shutil.which("solve-field")
    if not solve:
        raise FileNotFoundError("Astrometry.net solve-file exectuable not found")

    if isinstance(args, str):
        opts = args.split(" ")
    elif args is None:
        args = []
    # %% build command
    cmd = [solve, "--overwrite", str(fitsfn)]
    cmd += opts
    print("\n", " ".join(cmd), "\n")
    # %% execute
    ret = subprocess.check_output(cmd, universal_newlines=True)

    # solve-field returns 0 even if it didn't solve!
    print(ret)
    fitsfn.with_suffix(".log").write_text(" ".join(cmd) + "\n\n" + ret)
    if "Did not solve" in ret:
        logging.error(f"could not solve {fitsfn}")
        return False
    else:
        return True


def fits2azel(
    fitsfn: Path,
    *,
    wcsfn: Path = None,
    latlon: tuple[float, float] = None,
    time: datetime = None,
    solve: bool = False,
    args: str = None,
) -> xarray.Dataset:

    fitsfn = Path(fitsfn).expanduser()

    radec = fits2radec(fitsfn, wcsfn, solve, args)
    if radec is None:
        return None
    # if az/el can be computed, scale is implicitly merged with radec.
    scale = radec2azel(radec, latlon, time)
    if scale is None:
        scale = radec

    return scale
