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
from astropy.io import fits
from astropy.wcs import wcs

try:
    import pymap3d
except ImportError:
    pymap3d = None

__all__ = ["fits2radec", "fits2azel", "doSolve"]


def fits2radec(fitsfn: Path, solve: bool = False, args: str | None = None):
    """
    get RA, Decl from FITS file
    """
    fitsfn = Path(fitsfn).expanduser()

    if solve and not doSolve(fitsfn, args):
        raise RuntimeError(f"{fitsfn} was not solved")

    with fits.open(fitsfn, mode="readonly") as f:
        yPix, xPix = f[0].shape[-2:]

        x, y = meshgrid(range(xPix), range(yPix))
        # pixel indices to find RA/dec of
        xy = column_stack((x.ravel(order="C"), y.ravel(order="C")))
        # %% use astropy.wcs to register pixels to RA/DEC
        """
        http://docs.astropy.org/en/stable/api/astropy.wcs.WCS.html#astropy.wcs.WCS
        naxis=[0,1] is to take x,y axes in case a color photo was input e.g. to astrometry.net cloud solver
        """
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
    scale["az"] = (("y", "x"), az)
    scale["el"] = (("y", "x"), el)
    scale.attrs["lat"] = latlon[0]
    scale.attrs["lon"] = latlon[1]
    scale.attrs["time"] = time

    return scale


def doSolve(fitsfn: Path, args: str | None = None) -> bool:
    """
    run Astrometry.net solve-field from Python
    """

    fitsfn = Path(fitsfn).expanduser()
    if not fitsfn.is_file():
        raise FileNotFoundError(f"{fitsfn} not found")

    if not (solve := shutil.which("solve-field")):
        raise FileNotFoundError("Astrometry.net solve-file exectuable not found")

    if isinstance(args, str):
        opts: list[str] = args.split(" ")
    elif args is None:
        opts = ["-v"]
    # %% build command
    cmd = [solve, "--overwrite", str(fitsfn)]
    cmd += opts
    print("\n", " ".join(cmd), "\n")
    # %% execute
    ret = subprocess.check_output(cmd, text=True)

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
    latlon: tuple[float, float],
    time: datetime,
    solve: bool = False,
    args: str | None = None,
):
    fitsfn = Path(fitsfn).expanduser()

    radec = fits2radec(fitsfn, solve, args)

    return radec2azel(radec, latlon, time)
