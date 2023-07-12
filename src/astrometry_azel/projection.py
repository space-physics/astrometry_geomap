"""
Created on Fri Sep 28 11:43:24 2018 by Sebastijan Mrak

Updated by Michael Hirsch
"""

from __future__ import annotations
import numpy as np
from datetime import datetime
from scipy.spatial import Delaunay
from scipy.interpolate import griddata


def interpolateCoordinate(x, N: int = 512, method: str = "linear"):
    """
    x: numpy.ndarray
        2D array of coordinates
        xarray.Data* is not compatible; use .data method to pop out numpy.ndarray
    N: int
        Number of points in the new grid
    method: str
        Interpolation method. Default is 'linear'
    """
    x0, y0 = np.meshgrid(np.arange(x.shape[0]), np.arange(x.shape[1]), indexing="ij")

    mask = np.ma.masked_invalid(x)
    x0 = x0[~mask.mask]
    y0 = y0[~mask.mask]
    X = x[~mask.mask]

    x1, y1 = np.meshgrid(np.arange(N), np.arange(N))

    return griddata((x0, y0), X.ravel(), (x1, y1), method=method)


def interpSpeedUp(x_in, y_in, image, N: int = 512, verbose: bool = True) -> tuple:
    """
    The speedup is based on the scipy.interpolate.griddata algorithm. Thorough
    explanation is on the stackoverflow
    https://stackoverflow.com/questions/20915502/speedup-scipy-griddata-for-multiple-interpolations-between-two-irregular-grids
    """

    def _interpolate(values, vtx, wts, fill_value=np.nan):
        ret = np.einsum("nj,nj->n", np.take(values, vtx), wts)
        ret[np.any(wts < 0, axis=1)] = fill_value
        return ret

    def _interpWeights(xyz, uvw, d: int = 2):
        tri = Delaunay(xyz)
        simplex = tri.find_simplex(uvw)
        vertices = np.take(tri.simplices, simplex, axis=0)
        temp = np.take(tri.transform, simplex, axis=0)
        delta = uvw - temp[:, d]
        bary = np.einsum("njk,nk->nj", temp[:, :d, :], delta)
        return vertices, np.hstack((bary, 1 - bary.sum(axis=1, keepdims=True)))

    # Get the valid pixels, ie: np.isifinite() indexing
    if image.ndim == 3:
        provisional_image = image[0]
    elif image.ndim == 2:
        provisional_image = image
    else:
        raise ValueError("expected image or image stack")
    mask = np.ma.masked_invalid(provisional_image)
    # Make new grids constraint by input longitude/latitude boundaries and resolution N
    xgrid, ygrid = np.meshgrid(
        np.linspace(np.nanmin(x_in), np.nanmax(x_in), N),
        np.linspace(np.nanmin(y_in), np.nanmax(y_in), N),
    )
    # Old Coordinates maked -> flattern to a 1D array
    x = x_in[~mask.mask]
    y = y_in[~mask.mask]
    z = provisional_image[~mask.mask]
    # Old Coordinates -> To a single 2D array. x and y flattern to a single dimension
    xy = np.zeros([z.size, 2])
    xy[:, 0] = x
    xy[:, 1] = y
    # New Coordinates: Flattern into a 2D array. Same as for the old
    uv = np.zeros([xgrid.shape[0] * xgrid.shape[1], 2])
    uv[:, 0] = xgrid.flatten()
    uv[:, 1] = ygrid.flatten()
    # trinagulate to new grids, simplex wights for a new grid, barycentric
    # coordinates based on the simplex for the new grids are computed
    if verbose:
        print("Computing intepolation weights")
    t0 = datetime.now()
    vtx, wts = _interpWeights(xy, uv)
    # Interpolate N images
    Zim = np.copy(image) * np.nan
    if image.ndim == 3:
        if verbose:
            print("Interpolating", image.shape[0], "images")
        for i in range(image.shape[0]):
            Zim[i] = _interpolate(image[i], vtx, wts).reshape(N, N)
    else:
        Zim = _interpolate(image, vtx, wts).reshape(N, N)
    if verbose:
        print(f"Interpolation done in {(datetime.now() - t0).total_seconds()} seconds")
    # Return grids and interp points with associative weights

    return xgrid, ygrid, Zim
