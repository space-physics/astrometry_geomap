#!/usr/bin/env python
"""
http://astrometry.net/doc/readme.html#getting-index-files

Downloads 2MASS whole-sky index files, which worked well for me with a
variety of non-all-sky auroral imagagers in the 5 to 50 degree FOV range.
Also, the Tycho index files are good for this FOV range and I sometimes need them too.
"""
from astrometry_azel import download
from argparse import ArgumentParser

url_2mass = "http://broiler.astrometry.net/~dstn/4200/"
url_tycho = "http://broiler.astrometry.net/~dstn/4100/"


def main():
    p = ArgumentParser()
    p.add_argument(
        "-o",
        "--outdir",
        help="directory to save index files",
        default="~/astrometry-data",
    )
    p.add_argument("-source", default=url_2mass)
    p.add_argument(
        "-i",
        "--indexrange",
        help="start,stop (inclusive) index range",
        nargs=2,
        type=int,
        default=(8, 19),
    )
    P = p.parse_args()

    download(P.outdir, P.source, P.indexrange)


if __name__ == "__main__":
    main()
