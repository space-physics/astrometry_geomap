#!/usr/bin/env python
"""
Utility program to print source Coordinates in RA,DEC that astrometry.net found
use this with .rdls files after solving an image
"""
from astropy.io import fits

def sourceradec(fn):
    with fits.open(str(fn),'readonly') as f:
        return f[1].data


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="show RA DEC in .rdls files after solving an image")
    p.add_argument('fn',help='.rdls file from astrometry.net')
    p = p.parse_args()

    radec = sourceradec(p.fn)

    print('{} sources found in {}'.format(radec.shape[0], p.fn))

    print(radec)



