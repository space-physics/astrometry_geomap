import xarray
import numpy as np
import typing

from matplotlib.pyplot import figure
from matplotlib.colors import LogNorm
import cartopy


def geomap(img: xarray.Dataset, minimum_elevation: float = 0.0):
    """
    plot geomapped image

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

    ax: typing.Any = fg.add_subplot(projection=proj)

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
