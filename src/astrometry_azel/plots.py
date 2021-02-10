from pathlib import Path
import logging
import xarray
from matplotlib.figure import Figure
import numpy as np


def plotazel(scale: xarray.Dataset, plottype: str = "singlecontour", img: np.ndarray = None):

    if "az" not in scale:
        return None

    if plottype == "singlecontour":
        fg = Figure()
        ax = fg.gca()
        if img is not None:
            ax.imshow(img, origin="lower", cmap="gray")
        cs = ax.contour(scale["x"], scale["y"], scale["az"])
        ax.clabel(cs, inline=1, fmt="%0.1f")
        cs = ax.contour(scale["x"], scale["y"], scale["el"])
        ax.clabel(cs, inline=True, fmt="%0.1f")
        ax.set_xlabel("x-pixel")
        ax.set_ylabel("y-pixel")
        ax.set_title(
            f"{Path(scale.filename).name}  ({scale.lat:.2f}, {scale.lon:.2f})  {scale.time}\nAzimuth / Elevation"
        )
        fg.set_tight_layout(True)
        return fg
    elif plottype == "image":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        hia = ax[0].imshow(scale["az"], origin="lower")
        hc = fg.colorbar(hia)
        hc.set_label("Azimuth [deg]")
    elif plottype == "contour":
        fg = Figure(figsize=(12, 5))
        ax = fg.subplots(1, 2, sharey=True)
        if img is not None:
            ax[0].imshow(img, origin="lower", cmap="gray")
        cs = ax[0].contour(scale["x"], scale["y"], scale["az"])
        ax[0].clabel(cs, inline=1, fmt="%0.1f")

    ax[0].set_xlabel("x-pixel")
    ax[0].set_ylabel("y-pixel")
    ax[0].set_title("azimuth")
    # %%
    axe = ax[1]
    if plottype == "image":
        hie = axe.imshow(scale["el"], origin="lower")
        hc = fg.colorbar(hie)
        hc.set_label("Elevation [deg]")
    elif plottype == "contour":
        if img is not None:
            axe.imshow(img, origin="lower", cmap="gray")
        cs = axe.contour(scale["x"], scale["y"], scale["el"])
        axe.clabel(cs, inline=True, fmt="%0.1f")

    axe.set_xlabel("x-pixel")
    axe.set_title("elevation")
    fg.suptitle(f"{Path(scale.filename).name}\n({scale.lat:.2f}, {scale.lon:.2f})  {scale.time}")
    fg.set_tight_layout(True)

    return fg


def plotradec(scale: xarray.Dataset, plottype: str = "singlecontour", img: np.ndarray = None):

    if "ra" not in scale:
        return None

    if plottype == "singlecontour":
        fg = Figure()
        ax = fg.gca()
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


def plotimagestack(img: np.ndarray, fn: Path, clim=None):
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
