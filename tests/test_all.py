#!/usr/bin/env python
"""
http://nova.astrometry.net/user_images/1572720
"""
import pytest
from pathlib import Path
from pytest import approx
import shutil

import astrometry_azel as ael

rdir = Path(__file__).parent
ignore = "ignore:The WCS transformation has more axes"
LATLON = (0, 0)
TIME = "2000-01-01T00:00"
fitsfn = rdir / "apod4.fits"


@pytest.mark.skipif(
    shutil.which("solve-file"), reason="solve-field is actually present"
)
def test_nosolve(tmp_path):
    with pytest.raises(FileNotFoundError):
        ael.doSolve(tmp_path)


@pytest.mark.filterwarnings(ignore)
def test_fits2radec():
    scale = ael.fits2radec(fitsfn)

    assert scale["ra"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [152.313342, 157.988921, 165.012208]
    )
    assert scale["dec"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [59.982123, 59.182819, 59.149952]
    )


@pytest.mark.filterwarnings(ignore)
def test_fits2azel():
    pytest.importorskip("pymap3d")

    scale = ael.fits2azel(fitsfn, LATLON, TIME)

    assert scale["az"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [24.58404928, 26.84288277, 28.44059037]
    )
    assert scale["el"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [17.79638021, 15.74400771, 12.49648814]
    )


if __name__ == "__main__":
    pytest.main(["-x", __file__])
