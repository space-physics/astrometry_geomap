"""
Image stack -> average -> write FITS


average the specified frames then write a FITS file.
Averaging a selected stack of images improves SNR for astrometry.net
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
from datetime import datetime
import logging

from astropy.io import fits
import xarray

try:
    import imageio.v3 as iio
except ImportError:
    imageio = None  # type: ignore
try:
    import h5py
except ImportError:
    h5py = None
try:
    from scipy.io import loadmat
except ImportError:
    loadmat = None


def rgb2grey(rgb_img):
    """
    rgb_img: ndarray
        RGB image
    from PySumix rgb2gray.py
    """

    ndim = rgb_img.ndim
    if ndim == 2:
        logging.info("assuming its already gray since ndim=2")
        grey_img = rgb_img
    elif ndim == 3 and rgb_img.shape[-1] == 3:  # this is the normal case
        grey_img = np.around(rgb_img[..., :] @ [0.299, 0.587, 0.114]).astype(rgb_img.dtype)
    elif ndim == 3 and rgb_img.shape[-1] == 4:
        logging.info("assuming this is an RGBA image, discarding alpha channel")
        grey_img = rgb2grey(rgb_img[..., :-1])

    return grey_img


def read_data(in_file: Path):
    img = xarray.open_dataset(in_file)
    img["image"] = (("y", "x"), load_image(img.filename))

    return img


def load_image(file: Path):
    """
    load netCDF from PlateScale.py and original image

    Parameters
    ----------

    file: pathlib.Path
        netCDF file from PlateScale.py
    """

    file = Path(file).expanduser().resolve(strict=True)

    if file.suffix == ".fits":
        with fits.open(file, mode="readonly", memmap=False) as f:
            image = f[0].data
    else:
        image = rgb2grey(iio.imread(file))

    return image


def meanstack(
    infn: Path, Navg: slice | int, ut1: datetime | None = None, method: str = "mean"
) -> tuple:
    infn = Path(infn).expanduser().resolve()
    if not infn.is_file():
        raise FileNotFoundError(infn)

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
        raise ValueError(f"not sure how to handle Navg={Navg}")
    # %% load images
    """
    some methods handled individually to improve efficiency with huge files
    """
    if infn.suffix == ".h5":
        if h5py is None:
            raise ImportError("pip install h5py")
        img, ut1 = _h5mean(infn, ut1, key, method)
    elif infn.suffix in {".fits", ".new"}:
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
        if img.ndim in {3, 4} and img.shape[-1] == 3:  # assume RGB
            img = collapsestack(img, key, method)

    return img, ut1


def _h5mean(fn: Path, ut1: datetime | None, key: slice, method: str) -> tuple:
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


def collapsestack(img, key: slice, method: str):
    if img.ndim not in {2, 3, 4}:
        raise ValueError("only 2D, 3D, or 4D image stacks are handled")

    # %% 2-D
    if img.ndim == 2:
        return img
    # %% 3-D
    if method == "mean":
        func = np.mean
    elif method == "median":
        func = np.median  # type: ignore
    else:
        raise TypeError(f"unknown method {method}")

    colaps = func(img[key, ...], axis=0).astype(img.dtype)
    assert colaps.ndim > 0
    assert isinstance(colaps, np.ndarray)

    return colaps


def write_netcdf(ds: xarray.Dataset, out_file: Path) -> None:
    enc = {}

    for k in ds.data_vars:
        if ds[k].ndim < 2:
            continue

        enc[k] = {
            "zlib": True,
            "complevel": 3,
            "fletcher32": True,
            "chunksizes": tuple(map(lambda x: x // 2, ds[k].shape))
            # arbitrary, little impact on compression
        }

    ds.to_netcdf(out_file, format="NETCDF4", engine="netcdf4", encoding=enc)


def write_fits(img, outfn: Path) -> None:
    f = fits.PrimaryHDU(img)

    f.writeto(outfn, overwrite=True, checksum=True)
    # no close()
    print("writing", outfn)


def readh5coord(fn: Path) -> tuple[float, float] | None:
    with h5py.File(fn, "r") as f:
        try:
            latlon = (f["/sensorloc"]["glat"], f["/sensorloc"]["glon"])
        except KeyError:
            try:
                latlon = f["/lla"][:2]
            except KeyError:
                raise KeyError(f"could not find lat/lon in {fn}")

    return latlon
