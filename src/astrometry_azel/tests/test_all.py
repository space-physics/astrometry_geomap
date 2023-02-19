"""
http://nova.astrometry.net/user_images/1572720
"""
import pytest
from pathlib import Path
from pytest import approx
import shutil

import astrometry_azel as ael

rdir = Path(__file__).parent
LATLON = (0, 0)
TIME = "2000-01-01T00:00"
fitsfn = rdir / "apod4.fits"

exe = shutil.which("solve-field")


@pytest.mark.skipif(exe is None, reason="solve-field missing")
def test_nosolve(tmp_path):
    with pytest.raises(FileNotFoundError):
        ael.doSolve(tmp_path)


@pytest.mark.skipif(exe is None, reason="solve-field missing")
def test_solve():
    ael.doSolve(fitsfn)


def test_fits2radec():
    scale = ael.fits2radec(fitsfn)

    assert scale["ra"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [152.313342, 157.988921, 165.012208]
    )
    assert scale["dec"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [59.982123, 59.182819, 59.149952]
    )


def test_fits2azel():
    pytest.importorskip("pymap3d")

    scale = ael.fits2azel(fitsfn, latlon=LATLON, time=TIME)
    assert scale["az"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [24.58105122, 26.83990064, 28.43758228]
    )
    assert scale["el"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [17.79424959, 15.74175926, 12.49407394]
    )
