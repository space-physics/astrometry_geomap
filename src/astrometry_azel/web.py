from __future__ import annotations
from pathlib import Path
import urllib.request
import urllib.error
import socket


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
        try:
            urllib.request.urlretrieve(url, str(outfile))
        except (socket.gaierror, urllib.error.URLError) as err:
            raise ConnectionError("could not download {} due to {}".format(url, err))
