#!/usr/bin/env python3
"""
http://astrometry.net/doc/readme.html#getting-index-files

Downloads 2MASS whole-sky index files, which worked well for me with a
variety of non-all-sky auroral imagagers in the 5 to 50 degree FOV range.
Also, the Tycho index files are good for this FOV range and I sometimes need them too.
"""

from __future__ import annotations
from argparse import ArgumentParser
from pathlib import Path
import urllib.request
import urllib.error

url_2mass = "http://broiler.astrometry.net/~dstn/4200/"
url_tycho = "http://broiler.astrometry.net/~dstn/4100/"


def download(odir: Path, source_url: str, irng: list[int]):
    """Download star index files.
    The default range was useful for my cameras.
    """

    assert len(irng) == 2, "specify start, stop indices"

    odir = Path(odir).expanduser()
    odir.mkdir(parents=True, exist_ok=True)

    ri = int(source_url.split("/")[-2][:2])

    for i in range(irng[0], irng[1] + 1):
        fn = f"index-{ri:2d}{i:02d}.fits"
        url = f"{source_url}{fn}"
        ofn = odir / fn
        if ofn.is_file():  # no clobber
            print("Exists:", ofn)
            continue
        print(f"{url} => {ofn}")

        url_retrieve(url, ofn)


def url_retrieve(url: str, outfile: Path, overwrite: bool = False):
    """
    Parameters
    ----------
    url: str
        URL to download from
    outfile: pathlib.Path
        output filepath (including name)
    overwrite: bool
        overwrite if file exists
    """

    outfile = Path(outfile).expanduser().resolve()
    if outfile.is_dir():
        raise ValueError("Please specify full filepath, including filename")
    # need .resolve() in case intermediate relative dir doesn't exist
    if overwrite or not outfile.is_file():
        outfile.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, outfile)


p = ArgumentParser()
p.add_argument("-o", "--outdir", help="directory to save index files", default="~/astrometry-data")
p.add_argument("-source", nargs="+", default=[url_2mass, url_tycho])
p.add_argument(
    "-i",
    "--indexrange",
    help="start,stop (inclusive) index range",
    nargs=2,
    type=int,
    default=(8, 19),
)
P = p.parse_args()

for s in P.source:
    download(P.outdir, s, P.indexrange)
