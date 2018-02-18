#!/usr/bin/env python
"""
Utility program to print source Coordinates in RA,DEC that astrometry.net found
use this with .rdls files after solving an image
"""
from pathlib import Path
import logging
from astropy.io import fits

def sourceradec(fn):
    fn = Path(fn).expanduser()
    if fn.suffix != '.rdls':
        logging.error('this function is for .rdls files only')

    with fits.open(fn, 'readonly') as f:
        return f[1].data


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="show RA DEC in .rdls files after solving an image")
    p.add_argument('fn',help='.rdls file from astrometry.net')
    p = p.parse_args()

    radec = sourceradec(p.fn)

    print(radec.shape[0],'sources found in',p.fn,'with ra,dec coordinates:')

    print(radec)



