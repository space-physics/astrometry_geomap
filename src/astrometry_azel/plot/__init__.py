from pathlib import Path
import logging
import typing

import numpy as np
from astropy.io import fits
from astropy.wcs import wcs

from matplotlib.figure import Figure
from matplotlib.colors import LogNorm


def az_el(scale, plottype: str = "singlecontour", img=None):
    """
    plot azimuth and elevation mapped to sky
    """
    if plottype == "singlecontour":
        fg: typing.Any = Figure()
        ax: typing.Any = fg.gca()
        if img is not None:
            ax.imshow(img, origin="lower", cmap="gray")
        cs = ax.contour(scale["x"], scale["y"], scale["azimuth"])
        ax.clabel(cs, inline=1, fmt="%0.1f")
        cs = ax.contour(scale["x"], scale["y"], scale["elevation"])
        ax.clabel(cs, inline=True, fmt="%0.1f")
        ax.set_xlabel("x-pixel")
        ax.set_ylabel("y-pixel")
        ax.set_title(
            f"{Path(scale.filename).name}  ({scale.observer_latitude:.2f}, {scale.observer_longitude:.2f})"
            f"  {scale.time}  Azimuth / Elevation",
            wrap=True,
        )
        fg.set_tight_layout(True)
        return fg
    elif plottype == "image":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        hia = ax[0].imshow(scale["azimuth"], origin="lower")
        hc = fg.colorbar(hia)
        hc.set_label("Azimuth [deg]")
    elif plottype == "contour":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        if img is not None:
            ax[0].imshow(img, origin="lower", cmap="gray")
        cs = ax[0].contour(scale["x"], scale["y"], scale["azimuth"])
        ax[0].clabel(cs, inline=1, fmt="%0.1f")

    ax[0].set_xlabel("x-pixel")
    ax[0].set_ylabel("y-pixel")
    ax[0].set_title("azimuth")
    # %%
    axe = ax[1]
    if plottype == "image":
        hie = axe.imshow(scale["elevation"], origin="lower")
        hc = fg.colorbar(hie)
        hc.set_label("Elevation [deg]")
    elif plottype == "contour":
        if img is not None:
            axe.imshow(img, origin="lower", cmap="gray")
        cs = axe.contour(scale["x"], scale["y"], scale["elevation"])
        axe.clabel(cs, inline=True, fmt="%0.1f")

    axe.set_xlabel("x-pixel")
    axe.set_title("elevation")
    fg.suptitle(
        f"{Path(scale.filename).name} ({scale.observer_latitude:.2f}, {scale.observer_longitude:.2f})"
        f"  {scale.time}",
        wrap=True,
    )
    fg.set_tight_layout(True)

    return fg


def ra_dec(scale, plottype: str = "singlecontour", img=None):
    """
    plot right ascension and declination mapped to sky
    """
    if "ra" not in scale:
        return None

    if plottype == "singlecontour":
        fg: typing.Any = Figure()
        ax: typing.Any = fg.gca()
        if img is not None:
            ax.imshow(img, origin="lower", cmap="gray")
        cs = ax.contour(scale["x"], scale["y"], scale["ra"])
        ax.clabel(cs, inline=1, fmt="%0.1f")
        cs = ax.contour(scale["x"], scale["y"], scale["dec"])
        ax.clabel(cs, inline=True, fmt="%0.1f")
        ax.set_xlabel("x-pixel")
        ax.set_ylabel("y-pixel")
        ax.set_title(f"{Path(scale.filename).name}   Right Ascension / Declination")
        fg.set_tight_layout(True)
        return fg
    elif plottype == "image":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        hri = ax[0].imshow(scale["ra"], origin="lower")
        hc = fg.colorbar(hri)
        hc.set_label("RA [deg]")
    elif plottype == "contour":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        if img is not None:
            ax[0].imshow(img, origin="lower", cmap="gray")
        cs = ax[0].contour(scale["x"], scale["y"], scale["ra"])
        ax[0].clabel(cs, inline=1, fmt="%0.1f")

    ax[0].set_xlabel("x-pixel")
    ax[0].set_ylabel("y-pixel")
    ax[0].set_title("Right Ascension ")
    # %%
    if plottype == "image":
        hdi = ax[1].imshow(scale["dec"], origin="lower")
        hc = fg.colorbar(hdi)
        hc.set_label("Dec [deg]")
    elif plottype == "contour":
        if img is not None:
            ax[1].imshow(img, origin="lower", cmap="gray")
        cs = ax[1].contour(scale["x"], scale["y"], scale["dec"])
        ax[1].clabel(cs, inline=1, fmt="%0.1f")

    ax[1].set_xlabel("x-pixel")
    ax[1].set_title("Declination")
    fg.suptitle(Path(scale.filename).name)

    fg.set_tight_layout(True)

    return fg


def image_stack(img, fn: Path, clim=None):
    """
    plot image
    """
    fn = Path(fn).expanduser()
    # %% plotting
    if img.ndim == 3 and img.shape[0] == 3:  # it seems to be an RGB image
        cmap = None
        imnorm = None
        img = img.transpose([1, 2, 0])  # imshow() needs colors to be last axis
    else:
        cmap = "gray"
        imnorm = None
        # imnorm = LogNorm()

    fg = Figure()
    ax = fg.gca()
    if clim is None:
        hi = ax.imshow(img, origin="lower", interpolation="none", cmap=cmap, norm=imnorm)
    else:
        hi = ax.imshow(
            img,
            origin="lower",
            interpolation="none",
            cmap=cmap,
            vmin=clim[0],
            vmax=clim[1],
            norm=imnorm,
        )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(str(fn))
    if cmap is not None:
        try:
            hc = fg.colorbar(hi)
            hc.set_label(f"Data numbers {img.dtype}")
        except ValueError as e:
            logging.warning(f"trouble making picture colorbar  {e}")

    plotFN = fn.parent / (fn.stem + "_picture.png")
    print("writing", plotFN)
    fg.savefig(plotFN)


def add_image(fn: Path, cm, ax, alpha=1):
    """
    Astrometry.net makes file ".new" with the image and the WCS SIP 2-D polynomial fit coefficients in the FITS header

    We use DECL as "x" and RA as "y".
    pcolormesh() is used as it handles arbitrary pixel shapes.
    Note that pcolormesh() cannot tolerate NaN in X or Y (NaN in C is OK).

    https://github.com/scivision/python-matlab-examples/blob/main/PlotPcolor/pcolormesh_NaN.py
    """

    fn = Path(fn).expanduser().resolve(True)

    with fits.open(fn, mode="readonly", memmap=False) as f:
        img = f[0].data

        yPix, xPix = f[0].shape[-2:]
        x, y = np.meshgrid(range(xPix), range(yPix))  # pixel indices to find RA/dec of
        xy = np.column_stack((x.ravel(order="C"), y.ravel(order="C")))

        radec = wcs.WCS(f[0].header).all_pix2world(xy, 0)

    ra = radec[:, 0].reshape((yPix, xPix), order="C")
    dec = radec[:, 1].reshape((yPix, xPix), order="C")

    ax.set_title(fn.name)
    ax.pcolormesh(ra, dec, img, alpha=alpha, cmap=cm, norm=LogNorm())
    ax.set_ylabel("Right Ascension [deg.]")
    ax.set_xlabel("Declination [deg.]")
