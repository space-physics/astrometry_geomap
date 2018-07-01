#!/usr/bin/env python
"""
Utility program to print source Coordinates in RA,DEC that astrometry.net found
use this with .rdls files after solving an image
"""
from pathlib import Path
import logging
from astropy.io import fits
from argparse import ArgumentParser


def sourceradec(fn: Path):
    fn = Path(fn).expanduser()
    if fn.suffix != '.rdls':
        logging.warning('this function is for .rdls files only')

    with fits.open(fn, 'readonly') as f:
        return f[1].data


def main():
    p = ArgumentParser(description="show RA DEC in .rdls files after solving an image")
    p.add_argument('fn', help='.rdls file from astrometry.net')
    p = p.parse_args()

    radec = sourceradec(p.fn)

    print(radec.shape[0], 'sources found in', p.fn, 'with ra,dec coordinates:')

    print(radec)


if __name__ == '__main__':
    main()
