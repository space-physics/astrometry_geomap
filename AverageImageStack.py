#!/usr/bin/env python3
"""
aveage multi frame image stacks to improve SNR
"""

import imageio
from pathlib import Path
import typing
import numpy as np
import argparse

import astrometry_azel.io as aio


def stackcollapse(imgfn: Path, inds: typing.Sequence[int]):
    imgs = np.asarray(imageio.mimread(imgfn))

    for i in range(len(inds) - 1):
        yield aio.collapsestack(imgs, slice(inds[i], inds[i + 1]), method="mean")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("imgfn", help="multi-image file e.g. animated giff, TIFF, etc")
    p.add_argument("slice", help="start, stop, step", nargs=3, type=int)
    p.add_argument("-o", "--outpath")
    P = p.parse_args()

    imgfn = Path(P.imgfn).expanduser()
    outpath = Path(P.outpath).expanduser() if P.outpath else imgfn.parent

    for i, img in enumerate(stackcollapse(P.imgfn, list(range(*P.slice)))):
        outfn = outpath / f"{imgfn.stem}_{i}.png"
        print("writing", outfn)
        imageio.imwrite(outfn, img)
