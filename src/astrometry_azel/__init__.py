from pathlib import Path
from datetime import datetime
from datetime import timezone as tz
import functools
import shutil
import shlex
import subprocess

import numpy as np
import xarray

import logging

from astropy.time import Time
from astropy.coordinates import AltAz, Angle, EarthLocation, SkyCoord
from astropy import units as u
from astropy.io import fits
import astropy.wcs as awcs

__all__ = ["fits2azel", "fits2radec", "radec2azel", "doSolve"]

__version__ = "1.4.1"


def fits2radec(
    fitsfn: Path, solve: bool = False, args: str = "", index_dir: str | None = None
) -> xarray.Dataset:
    """
    get RA, Decl from FITS file
    """
    fitsfn = Path(fitsfn).expanduser()

    if solve:
        doSolve(fitsfn, args, index_dir=index_dir)

    with fits.open(fitsfn, mode="readonly") as f:
        yPix, xPix = f[0].shape[-2:]

    x, y = np.meshgrid(range(xPix), range(yPix))
    # pixel indices to find RA/dec of
    xy = np.column_stack((x.ravel(order="C"), y.ravel(order="C")))

    if not (wcsfn := fitsfn.with_suffix(".wcs")).is_file():
        if not (wcsfn := fitsfn.with_name("wcs.fits")).is_file():
            raise FileNotFoundError(f"could not find WCS file for {fitsfn}")
    with fits.open(wcsfn, mode="readonly") as f:
        # %% use astropy.wcs to register pixels to RA/DEC
        # https://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html#astropy.wcs.WCS
        # NOTE: it's normal to get this warning:
        # WARNING: FITSFixedWarning: The WCS transformation has more axes (2) than the image it is associated with (0) [astropy.wcs.wcs]
        if f[0].header["WCSAXES"] == 2:
            # greyscale image
            radec = awcs.wcs.WCS(f[0].header).all_pix2world(xy, 0)
        elif f[0].header["WCSAXES"] == 3:
            # color image
            radec = awcs.wcs.WCS(f[0].header, naxis=[0, 1]).all_pix2world(xy, 0)
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


def fits2azel(
    fitsfn: Path,
    *,
    latlon: tuple[float, float],
    time: datetime,
    solve: bool = False,
    args: str = "",
    index_dir: str | None = None,
):
    fitsfn = Path(fitsfn).expanduser()

    radec = fits2radec(fitsfn, solve, args, index_dir=index_dir)

    return radec2azel(radec, latlon, time)


def radec2azel(scale: xarray.Dataset, latlon: tuple[float, float], time: datetime):
    """
    right ascension/declination to azimuth/elevation
    """

    match time:
        case datetime():
            pass
        case float() | int():  # assume UT1_Unix
            time = datetime.fromtimestamp(time, tz=tz.UTC)
        case str():
            time = datetime.fromisoformat(time)
        case _:
            raise TypeError(f"expected datetime, float, int, or str -- got {type(time)}")

    print("image time:", time)
    # %% knowing camera location, time, and sky coordinates observed, convert to az/el for each pixel
    # .values is to avoid silently freezing AstroPy

    az, el = pymap3d_radec2azel(scale["ra"].values, scale["dec"].values, *latlon, time)
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
    scale["time"] = np.datetime64(time)

    return scale


def pymap3d_radec2azel(
    ra_deg,
    dec_deg,
    lat_deg,
    lon_deg,
    time: datetime,
) -> tuple:
    """
    sky coordinates (ra, dec) to viewing angle (az, el)

    Parameters
    ----------
    ra_deg : float
         ecliptic right ascension (degress)
    dec_deg : float
         ecliptic declination (degrees)
    lat_deg : float
              observer latitude [-90, 90]
    lon_deg : float
              observer longitude [-180, 180] (degrees)
    time : datetime.datetime
           time of observation

    Returns
    -------
    az_deg : float
             azimuth [degrees clockwize from North]
    el_deg : float
             elevation [degrees above horizon (neglecting aberration)]
    """

    obs = EarthLocation(lat=lat_deg * u.deg, lon=lon_deg * u.deg)
    points = SkyCoord(Angle(ra_deg, unit=u.deg), Angle(dec_deg, unit=u.deg), equinox="J2000.0")
    altaz = points.transform_to(AltAz(location=obs, obstime=Time(time)))

    return altaz.az.degree, altaz.alt.degree


@functools.cache
def get_solve_exe() -> str | None:
    return shutil.which("solve-field")


def doSolve(fitsfn: Path, args: str = "", index_dir: str | None = None) -> None:
    """
    run Astrometry.net solve-field from Python
    """

    fitsfn = Path(fitsfn).expanduser().resolve(strict=True)
    if not fitsfn.is_file():
        raise FileNotFoundError(f"{fitsfn} is not a specific file")

    # %% build command
    exe = get_solve_exe()
    if exe is None:
        raise FileNotFoundError("solve-field executable not found in PATH")

    cmd = [exe, "--overwrite", str(fitsfn), "--verbose"]

    if index_dir:
        if not Path(index_dir).is_dir():
            raise NotADirectoryError(f"{index_dir} is not a directory")
        cmd += ["--index-dir", str(index_dir)]

    if args:
        # if args is a string, split it. Don't append an empty space or solve-field CLI fail
        cmd += shlex.split(args)

    print("\n", " ".join(cmd), "\n")
    # %% execute, with live progress output

    with subprocess.Popen(cmd) as p:
        p.wait()
        if p.returncode != 0:
            raise RuntimeError(f"solve-field failed with exit code {p.returncode}")
