#!/usr/bin/env python
"""
http://nova.astrometry.net/user_images/1572720
"""
import pytest
from pathlib import Path
from numpy.testing import assert_allclose
#
from astrometry_azel import fits2azel

rdir = Path(__file__).parent


def test_fits2azel():
    fitsfn = rdir / 'apod4.fits'
    time = '2000-01-01T00:00:00'

    camLatLon = (40, -80)  # not true, just a guess
    scale = fits2azel(fitsfn, camLatLon, time, True)

    assert_allclose(scale['ra'].values[[32, 51, 98], [28, 92, 156]], [152.313342, 157.988921, 165.012208])
    assert_allclose(scale['dec'].values[[32, 51, 98], [28, 92, 156]], [59.982123, 59.182819, 59.149952])
    assert_allclose(scale['az'].values[[32, 51, 98], [28, 92, 156]], [22.794418, 20.788267, 17.572719])
    assert_allclose(scale['el'].values[[32, 51, 98], [28, 92, 156]], [17.359846, 15.084063, 13.287209])


if __name__ == '__main__':
    pytest.main()
