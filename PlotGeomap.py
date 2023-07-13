#!/usr/bin/env python3
"""
Use output netCDF from PlateScale.py to plot image as if the photons emitted at a single altitude.
This technique is used in aeronomy for aurora and airglow.
"""

from __future__ import annotations
import argparse
from pathlib import Path

import xarray
import numpy as np

from matplotlib.pyplot import figure, show
from matplotlib.colors import LogNorm
import cartopy

import pymap3d as pm

from astrometry_azel.io import load_image, write_netcdf


def project_image(img: xarray.Dataset, projection_altitude_km: float, observer_altitude_m: float):
    """
    project image to projection_altitude_km

    adapted from https://github.com/space-physics/dascasi
    """

    slant_range_m = projection_altitude_km * 1e3 / np.sin(np.radians(img["elevation"]))
    # secant approximation

    lat, lon, _ = pm.aer2geodetic(
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


def plot_geomap(img: xarray.Dataset, minimum_elevation: float = 0.0):
    """

    Parameters
    ----------

    img: xarray.Dataset
        image data and coordinates
    minimum_elevation: float
        minimum elevation angle to mask (degrees)
    """

    projection_altitude_km = img["latitude_proj"].attrs["projection_altitude_km"]

    proj = cartopy.crs.PlateCarree()

    elevation_mask = img.elevation.data < minimum_elevation
    masked = np.ma.masked_array(img.image, mask=elevation_mask)  # type: ignore

    # fg2 = figure()
    # axi = fg2.add_subplot()
    # axi.pcolormesh(masked, norm=LogNorm())
    # show()

    fg = figure()

    ax = fg.add_subplot(projection=proj)

    # plot observer
    ax.scatter(img.observer_longitude, img.observer_latitude, transform=proj, color="r", marker="*")

    hgl = ax.gridlines(crs=proj, color="gray", linestyle="--", linewidth=0.5)

    # features to give human sense of maps
    features = {
        "Thunder Mountain": (52.6, -124.27),
        "Calgary": (51.05, -114.08),
        "Banff": (51.18, -115.57),
        "Edmonton": (53.55, -113.49),
    }
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.LAND)

    states_provinces = cartopy.feature.NaturalEarthFeature(
        category="cultural", name="admin_1_states_provinces_lines", scale="50m", facecolor="none"
    )
    ax.add_feature(states_provinces, edgecolor="gray", linewidth=0.5)

    for k, v in features.items():
        ax.scatter(v[1], v[0], transform=proj, color="grey", marker="o", alpha=0.8)
        ax.text(v[1], v[0], k, transform=proj, alpha=0.8)

    # prettify figure
    latitude = np.ma.masked_array(img.latitude_proj, mask=elevation_mask)  # type: ignore
    longitude = np.ma.masked_array(img.longitude_proj, mask=elevation_mask)  # type: ignore
    lat_bounds = (latitude.min() - 0.5, latitude.max() + 0.5)
    lon_bounds = (longitude.min() - 0.5, longitude.max() + 0.5)
    hgl.bottom_labels = True
    hgl.left_labels = True

    ax.pcolormesh(img.longitude_proj, img.latitude_proj, masked, norm=LogNorm(), cmap="Greys_r")

    ax.set_title(
        f"{str(img.time.values)[:-10]}\n"
        f"Projection alt. (km): {projection_altitude_km}  "
        f"Min. Elv. (deg): {minimum_elevation}"
    )
    ax.set_xlabel("geographic longitude")
    ax.set_ylabel("geographic latitude")

    lims = (*lon_bounds, *lat_bounds)
    ax.set_extent(lims)

    return fg


def read_data(in_file: Path):
    img = xarray.open_dataset(in_file)
    img["image"] = (("y", "x"), load_image(img.filename))

    return img


p = argparse.ArgumentParser(
    description="plot geomap of image as if photons emitted at a single altitude"
)
p.add_argument("in_file", help="netCDF file from PlateScale.py")
p.add_argument("projection_altitude_km", type=float, help="altitude of emission (kilometers)")
p.add_argument(
    "-minel", "--minimum_elevation", type=float, default=0.0, help="minimum elevation (degrees)"
)
p.add_argument(
    "-obsalt",
    "--observer_altitude_m",
    type=float,
    help="altitude of observer (meters)",
    default=0.0,
)
P = p.parse_args()

in_file = Path(P.in_file).expanduser()

img = read_data(in_file)

img = project_image(img, P.projection_altitude_km, P.observer_altitude_m)

out_file = in_file.parent / (in_file.stem + "_proj.nc")
print("Save projected data to", out_file)
write_netcdf(img, out_file)

fig = plot_geomap(img, P.minimum_elevation)

figure_fn = in_file.parent / (in_file.stem + "_proj.png")
print("Save projected image to", figure_fn)
fig.savefig(figure_fn)

show()
