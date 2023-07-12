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

from astrometry_azel.io import load_image


def project_image(img: xarray.Dataset, altitude_km: float, observer_altitude_m: float):
    """
    project image to specified altitude_km

    adapted from https://github.com/space-physics/dascasi
    """

    slant_range = altitude_km * 1e3 / np.sin(np.radians(img["elevation"]))
    # secant approximation

    lat, lon, _ = pm.aer2geodetic(
        az=img["azimuth"],
        el=img["elevation"],
        srange=slant_range,
        lat0=img["observer_latitude"].item(),  # degrees north
        lon0=img["observer_longitude"].item(),  # degrees east
        h0=observer_altitude_m,  # meters
    )

    # lat, lon cannot be dimensions here because they're each dynamic in 2-D
    img.coords["latitude"] = (("y", "x"), lat)
    img.coords["longitude"] = (("y", "x"), lon)
    img.attrs["mapping_alt_km"] = altitude_km

    return img


def plot_geomap(img: xarray.Dataset, minimum_elevation: float = 0.0):
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
    latitude = np.ma.masked_array(img.latitude, mask=elevation_mask)  # type: ignore
    longitude = np.ma.masked_array(img.longitude, mask=elevation_mask)  # type: ignore
    lat_bounds = (latitude.min() - 0.5, latitude.max() + 0.5)
    lon_bounds = (longitude.min() - 0.5, longitude.max() + 0.5)
    hgl.bottom_labels = True
    hgl.left_labels = True

    ax.pcolormesh(img.longitude, img.latitude, masked, norm=LogNorm(), cmap="Greys_r")

    ax.set_title(f"{str(img.time.values)[:-10]} at {img.mapping_alt_km} km altitude")
    ax.set_xlabel("geographic longitude")
    ax.set_ylabel("geographic latitude")

    lims = (*lon_bounds, *lat_bounds)
    ax.set_extent(lims)

    return fg


p = argparse.ArgumentParser(
    description="plot geomap of image as if photons emitted at a single altitude"
)
p.add_argument("netcdf_file", help="netCDF file from PlateScale.py")
p.add_argument("altitude_km", type=float, help="altitude of emission (kilometers)")
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

netcdf_file = Path(P.netcdf_file).expanduser()

img = xarray.open_dataset(netcdf_file)
img["image"] = (("y", "x"), load_image(img.filename))

img = project_image(img, P.altitude_km, P.observer_altitude_m)

fig = plot_geomap(img, P.minimum_elevation)

figure_fn = netcdf_file.parent / (netcdf_file.stem + "_geomap.png")
print("Geomap saved to", figure_fn)
fig.savefig(figure_fn)

show()
