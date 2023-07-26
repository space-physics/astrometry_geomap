from __future__ import annotations
from pathlib import Path
from datetime import datetime

import xarray
import numpy as np

from .io import load_image, write_fits, write_netcdf
from .base import fits2azel

import pymap3d


def plate_scale(
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
    img = load_image(in_file)
    write_fits(img, new_file)

    scale = fits2azel(new_file, latlon=latlon, time=ut1, solve=solve, args=args)

    # %% write to file
    netcdf_file = Path(scale.filename).with_suffix(".nc")
    print("saving", netcdf_file)
    write_netcdf(scale, netcdf_file)

    return scale, img


def image_altitude(img: xarray.Dataset, projection_altitude_km: float, observer_altitude_m: float):
    """
    project image to projection_altitude_km

    adapted from https://github.com/space-physics/dascasi
    """

    slant_range_m = projection_altitude_km * 1e3 / np.sin(np.radians(img["elevation"]))
    # secant approximation

    lat, lon, _ = pymap3d.aer2geodetic(
        az=img["azimuth"],
        el=img["elevation"],
        srange=slant_range_m,  # meters
        lat0=img["observer_latitude"].item(),  # degrees north
        lon0=img["observer_longitude"].item(),  # degrees east
        h0=observer_altitude_m,  # meters
    )

    img.coords["latitude_proj"] = (("y", "x"), lat)
    img["latitude_proj"].attrs["projection_altitude_km"] = projection_altitude_km
    img["latitude_proj"].attrs["units"] = "degrees north WGS84"

    img.coords["longitude_proj"] = (("y", "x"), lon)
    img["longitude_proj"].attrs["projection_altitude_km"] = projection_altitude_km
    img["longitude_proj"].attrs["units"] = "degrees east WGS84"

    return img
