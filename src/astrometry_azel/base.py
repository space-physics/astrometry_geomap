from __future__ import annotations
from pathlib import Path
import subprocess
import shutil
import logging
from dateutil.parser import parse
from datetime import datetime
from numpy import meshgrid, column_stack, datetime64
import xarray
from astropy.io import fits
from astropy.wcs import wcs

try:
    import pymap3d
except ImportError:
    pymap3d = None

__all__ = ["fits2radec", "fits2azel", "doSolve"]


def fits2radec(fitsfn: Path, solve: bool = False, args: str = ""):
    """
    get RA, Decl from FITS file
    """
    fitsfn = Path(fitsfn).expanduser()

    if solve:
        doSolve(fitsfn, args)

    with fits.open(fitsfn, mode="readonly") as f:
        yPix, xPix = f[0].shape[-2:]

    x, y = meshgrid(range(xPix), range(yPix))
    # pixel indices to find RA/dec of
    xy = column_stack((x.ravel(order="C"), y.ravel(order="C")))

    if not (wcsfn := fitsfn.with_suffix(".wcs")).is_file():
        if not (wcsfn := fitsfn.with_name("wcs.fits")).is_file():
            raise FileNotFoundError(f"could not find WCS file for {fitsfn}")
    with fits.open(wcsfn, mode="readonly") as f:
        # %% use astropy.wcs to register pixels to RA/DEC
        # http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html#astropy.wcs.WCS
        # NOTE: it's normal to get this warning:
        # WARNING: FITSFixedWarning: The WCS transformation has more axes (2) than the image it is associated with (0) [astropy.wcs.wcs]
        if f[0].header["WCSAXES"] == 2:
            # greyscale image
            radec = wcs.WCS(f[0].header).all_pix2world(xy, 0)
        elif f[0].header["WCSAXES"] == 3:
            # color image
            radec = wcs.WCS(f[0].header, naxis=[0, 1]).all_pix2world(xy, 0)
        else:
            raise ValueError(f"{fitsfn} has {f[0].header['NAXIS']} axes -- expected 2 or 3")

    ra = radec[:, 0].reshape((yPix, xPix), order="C")
    dec = radec[:, 1].reshape((yPix, xPix), order="C")
    # %% collect output
    radec = xarray.Dataset(
        {"ra": (("y", "x"), ra), "dec": (("y", "x"), dec)},
        {"x": range(xPix), "y": range(yPix)},
        attrs={"filename": str(fitsfn)},
    )

    radec["ra"].attrs["units"] = "Right Ascension degrees east"
    radec["dec"].attrs["units"] = "Declination degrees north"
    radec["x"].attrs["units"] = "pixel index"
    radec["y"].attrs["units"] = "pixel index"

    return radec


def radec2azel(scale, latlon: tuple[float, float], time: datetime | None):
    if pymap3d is None:
        raise ImportError("azimuth, elevation computations require: pip install pymap3d")

    assert isinstance(scale, xarray.Dataset)

    if time is None:
        with fits.open(scale.filename, mode="readonly") as f:
            try:
                t = f[0].header["FRAME"]
                # NOTE: this only works from Solis FITS files
            except KeyError:
                raise ValueError("Could not determine time of image")
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
        )

    # %% collect output
    scale["azimuth"] = (("y", "x"), az)
    scale["azimuth"].attrs["units"] = "degrees clockwise from north"

    scale["elevation"] = (("y", "x"), el)
    scale["elevation"].attrs["units"] = "degrees above horizon"

    scale["observer_latitude"] = latlon[0]
    scale["observer_latitude"].attrs["units"] = "degrees north WGS84"

    scale["observer_longitude"] = latlon[1]
    scale["observer_longitude"].attrs["units"] = "degrees east WGS84"

    # datetime64 can be saved to netCDF4, but Python datetime.datetime cannot
    scale["time"] = datetime64(time)

    return scale


def doSolve(fitsfn: Path, args: str = "") -> None:
    """
    run Astrometry.net solve-field from Python
    """

    fitsfn = Path(fitsfn).expanduser()
    if not fitsfn.is_file():
        raise FileNotFoundError(f"{fitsfn} not found")

    if not (solve := shutil.which("solve-field")):
        raise FileNotFoundError("Astrometry.net solve-file exectuable not found")

    # %% build command
    cmd = [solve, "--overwrite", str(fitsfn), "--verbose"]
    if args:
        # if args is a string, split it. Don't append an empty space or solve-field CLI fail
        cmd += args.split(" ")
    print("\n", " ".join(cmd), "\n")
    # %% execute
    # bufsize=1: line-buffered
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, text=True) as p:
        for line in p.stdout:  # type: ignore
            print(line, end="")

    if "Did not solve" in line:
        raise RuntimeError(f"could not solve {fitsfn}")


def fits2azel(
    fitsfn: Path,
    *,
    latlon: tuple[float, float],
    time: datetime,
    solve: bool = False,
    args: str = "",
):
    fitsfn = Path(fitsfn).expanduser()

    radec = fits2radec(fitsfn, solve, args)

    return radec2azel(radec, latlon, time)
