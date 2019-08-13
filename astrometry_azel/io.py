#!/usr/bin/env python
"""
Astrometry-azel
Copyright (C) 2013-2018 Michael Hirsch, Ph.D.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------
Image stack -> average -> write FITS


Because ImageJ has been a little buggy about writing FITS files, in particular the header
that astrometry.net then crashes on, we wrote this quick script to ingest a variety
of files and average the specified frames then write a FITS.
The reason we average a selected stack of images is to reduce the noise for use in
astrometry.net

The error you might get from an ImageJ saved FITS when reading in:
PyFits, AstroPy, or ImageMagick is:
IOError: Header missing END card.
"""
from pathlib import Path
import numpy as np
from typing import Tuple, Optional
from datetime import datetime
from astropy.io import fits
import logging

try:
    import imageio
except ImportError:
    imageio = None
try:
    import h5py
except ImportError:
    h5py = None
try:
    from scipy.io import loadmat
except ImportError:
    loadmat = None


def meanstack(
    infn: Path, Navg: int, ut1: Optional[datetime] = None, method: str = "mean"
) -> Tuple[np.ndarray, Optional[datetime]]:

    infn = Path(infn).expanduser().resolve(strict=True)
    # %% parse indicies to load
    if isinstance(Navg, slice):
        key = Navg
    elif isinstance(Navg, int):
        key = slice(0, Navg)
    elif len(Navg) == 1:
        key = slice(0, Navg[0])
    elif len(Navg) == 2:
        key = slice(Navg[0], Navg[1])
    else:
        raise ValueError(f"not sure what you mean by Navg={Navg}")
    # %% load images
    """
    some methods handled individually to improve efficiency with huge files
    """
    if infn.suffix == ".h5":
        if h5py is None:
            raise ImportError("pip install h5py")
        img, ut1 = _h5mean(infn, ut1, key, method)
    elif infn.suffix in (".fits", ".new"):
        # mmap doesn't work with BZERO/BSCALE/BLANK
        with fits.open(infn, mode="readonly", memmap=False) as f:
            img = collapsestack(f[0].data, key, method)
    elif infn.suffix == ".mat":
        if loadmat is None:
            raise ImportError("pip install scipy")
        img = loadmat(infn)
        img = collapsestack(img["data"].T, key, method)  # matlab is fortran order
    else:  # .tif etc.
        if imageio is None:
            raise ImportError("pip install imageio")
        img = imageio.imread(infn, as_gray=True)
        if img.ndim in (3, 4) and img.shape[-1] == 3:  # assume RGB
            img = collapsestack(img, key, method)

    return img, ut1


def _h5mean(
    fn: Path, ut1: Optional[datetime], key: slice, method: str
) -> Tuple[np.ndarray, Optional[datetime]]:
    with h5py.File(fn, "r") as f:
        img = collapsestack(f["/rawimg"], key, method)
        # %% time
        if ut1 is None:
            try:
                ut1 = f["/ut1_unix"][key][0]
            except KeyError:
                pass
        # %% orientation
        try:
            img = np.rot90(img, k=f["/params"]["rotccw"])
        except KeyError:
            pass

    return img, ut1


def collapsestack(img: np.ndarray, key: slice, method: str) -> np.ndarray:
    if img.ndim not in (2, 3):
        raise ValueError("only 2D or 3D image stacks are handled")

    # %% 2-D
    if img.ndim == 2:
        return img
    # %% 3-D
    if method == "mean":
        func = np.mean
    elif method == "median":
        func = np.median
    else:
        raise TypeError(f"unknown method {method}")

    return func(img[key, ...], axis=0).astype(img.dtype)


def writefits(img: np.ndarray, outfn: Path):
    outfn = Path(outfn).expanduser()

    f = fits.PrimaryHDU(img)
    try:
        f.writeto(outfn, overwrite=False, checksum=True)
        # no close()
        print("writing", outfn)
    except OSError:
        logging.warning(f"did not overwrite existing {outfn}")


def readh5coord(fn: Path) -> Tuple[float, float]:
    if not fn.suffix == ".h5":
        return None

    with h5py.File(fn, "r") as f:
        try:
            latlon = (f["/sensorloc"]["glat"], f["/sensorloc"]["glon"])
        except KeyError:
            try:
                latlon = f["/lla"][:2]
            except KeyError:
                return None

    return latlon
