"""
Astrometry-azel
Copyright (C) 2013-2018 Michael Hirsch, Ph.D.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import requests
from pathlib import Path
from typing import Sequence
from .base import fits2azel, fits2radec, radec2azel, doSolve  # noqa: F401


def urlretrieve(url: str, fn: Path, overwrite: bool=False):
    if not overwrite and fn.is_file() and fn.stat().st_size > 10000:
        print(f'SKIPPED {fn}')
        return
# %% prepare to download
    R = requests.head(url, allow_redirects=True, timeout=10)
    if R.status_code != 200:
        logging.error(f'{url} not found. \n HTTP ERROR {R.status_code}')
        return
# %% download
    print(f'downloading {int(R.headers["Content-Length"])//1000000} MBytes:  {fn.name}')
    R = requests.get(url, allow_redirects=True, timeout=10)
    with fn.open('wb') as f:
        f.write(R.content)


def download(odir: Path, source_url: str, irng: Sequence[int]):
    """Download star index files.
    The default range was useful for my cameras.
    """
    assert len(irng) == 2, 'specify start, stop indices'

    odir = Path(odir).expanduser()
    odir.mkdir(parents=True, exist_ok=True)

    ri = int(source_url.split('/')[-2][:2])

    for i in range(*irng):
        fn = f'index-{ri:2d}{i:02d}.fits'
        url = f'{source_url}{fn}'
        ofn = odir / fn
        if ofn.is_file():  # no clobber
            print('skipping', ofn)
            continue
        print(f'{url} => {ofn}', end='\r')

        urlretrieve(url, ofn)
