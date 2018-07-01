#!/usr/bin/env python
"""
Downloads 2MASS whole-sky index files, which worked well for me with a
variety of non-all-sky auroral imagagers in the 5 to 50 degree FOV range.
Also, the Tycho index files are said to be good for this FOV range, but I don't
recall whether or not I tried them.
"""
from pathlib import Path
from typing import List
import urllib.error
import urllib.request
from argparse import ArgumentParser

url_2mass = 'http://broiler.astrometry.net/~dstn/4200/'
url_tycho = 'http://broiler.astrometry.net/~dstn/4100/'


def get_index(odir: Path, source_url: str, irng: List[int]):
    """Download star index files.
    The default range was useful for my cameras.
    """
    assert len(irng) == 2, 'specify start, stop indices'

    odir = Path(odir).expanduser()
    odir.mkdir(parents=True, exist_ok=True)

    ri = int(source_url.split('/')[-2][:2])

    for i in range(*irng):
        fn = f'index-{ri:2d}{i:02d}.fits'
        u = f'{source_url}{fn}'
        ofn = odir / fn
        if ofn.is_file():  # no clobber
            print('skipping', ofn)
            continue
        print(f'{u} => {ofn}', end='\r')

        try:
            urllib.request.urlretrieve(u, ofn)
        except urllib.error.URLError as e:
            raise OSError(f'Could not download {u}. Are you connected to the Internet?  \n{e}')


def main():
    p = ArgumentParser()
    p.add_argument('outdir', help='directory to save index files')
    p.add_argument('-source', default=url_2mass)
    p.add_argument('-indexrange', help='start,stop (inclusive) index range', nargs=2, type=int, default=(8, 19))
    P = p.parse_args()

    get_index(P.outdir, P.source, P.indexrange)


if __name__ == '__main__':
    main()
