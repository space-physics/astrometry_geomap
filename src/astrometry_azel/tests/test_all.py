"""
solves test image from
https://nova.astrometry.net/user_images/1572720
"""

import pytest
from pathlib import Path
from pytest import approx
import shutil

import astrometry_azel as ael

import importlib.resources as ir


def test_nosolve(tmp_path, index_dir):
    with pytest.raises(FileNotFoundError):
        ael.doSolve(tmp_path, index_dir=index_dir)

@pytest.fixture(scope="function")
def index_dir() -> Path:
    with ir.as_file(ir.files(f"{__package__}")) as pdir:
        return pdir.parent / "index_data"

@pytest.fixture(scope="function")
def fits_file(tmp_path) -> Path:
    with ir.as_file(ir.files(f"{__package__}") / "apod4.fits") as fits:
        shutil.copy(fits.with_suffix(".new"), tmp_path)
        shutil.copy(fits.with_suffix(".wcs"), tmp_path)

    return tmp_path / (fits.stem + ".new")


@pytest.mark.skipif(ael.get_solve_exe() is None, reason="solve-field missing")
def test_solve(tmp_path, index_dir):
    with ir.as_file(ir.files(f"{__package__}") / "apod4.fits") as fits:
        shutil.copy(fits, tmp_path)
        # --scale-low isn't needed, just to speed up CI test
        ael.doSolve(tmp_path / fits.name, args="--scale-low 20", index_dir=index_dir)


def test_fits2radec(fits_file):
    scale = ael.fits2radec(fits_file)

    ra_expected = [152.35248165, 157.96163129, 164.95871358]
    assert scale["ra"].values[[32, 51, 98], [28, 92, 156]] == approx(ra_expected, rel=0.01)

    dec_expected = [59.98073175, 59.20526844, 59.18426375]
    assert scale["dec"].values[[32, 51, 98], [28, 92, 156]] == approx(dec_expected, rel=0.01)


def test_fits2azel(fits_file):
    pytest.importorskip("pymap3d")

    scale = ael.fits2azel(fits_file, latlon=(0, 0), time="2000-01-01T00:00")

    az_expected = [24.59668217, 26.81546529, 28.39753029]
    assert scale["azimuth"].values[[32, 51, 98], [28, 92, 156]] == approx(az_expected, rel=0.01)

    el_expected = [17.78086795, 15.74570897, 12.50919858]
    assert scale["elevation"].values[[32, 51, 98], [28, 92, 156]] == approx(el_expected, rel=0.01)
