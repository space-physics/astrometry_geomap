#!/usr/bin/env python3
"""
Use output netCDF from PlateScale.py to plot image as if the photons emitted at a single altitude.
This technique is used in aeronomy for aurora and airglow.
"""

from __future__ import annotations
import argparse
from pathlib import Path

from matplotlib.pyplot import show

from astrometry_azel.io import read_data, write_netcdf
import astrometry_azel.project as project
import astrometry_azel.plot.project as plot_project


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

img = project.image_altitude(img, P.projection_altitude_km, P.observer_altitude_m)

out_file = in_file.parent / (in_file.stem + "_proj.nc")
print("Save projected data to", out_file)
write_netcdf(img, out_file)

fig = plot_project.geomap(img, P.minimum_elevation)

figure_fn = in_file.parent / (in_file.stem + "_proj.png")
print("Save projected image to", figure_fn)
fig.savefig(figure_fn)

show()
