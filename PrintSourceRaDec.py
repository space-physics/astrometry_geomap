#!/usr/bin/env python
"""
Utility program to print source Coordinates in RA,DEC that astrometry.net found
use this with .rdls files after solving an image
"""
from pathlib import Path
from astropy.io import fits
import argparse


def main():
    p = argparse.ArgumentParser(description="show RA DEC in .rdls files after solving an image")
    p.add_argument("fn", help=".rdls file from astrometry.net")
    p = p.parse_args()

    fn = Path(p.fn).expanduser().resolve(strict=True)
    with fits.open(fn, "readonly") as f:
        radec = f[1].data

    print(radec.shape[0], "sources found in", fn, "with ra,dec coordinates:")

    print(radec)


if __name__ == "__main__":
    main()
