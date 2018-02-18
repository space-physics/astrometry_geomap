#!/usr/bin/env python
"""
http://nova.astrometry.net/user_images/1572720
"""
from pathlib import Path
from numpy.testing import assert_allclose
import unittest
#
from astrometry_azel import fits2azel

rdir = Path(__file__).parent

class BasicTests(unittest.TestCase):

    def test_fits2azel(self):
        makeplot=['skipsolve']
        fitsfn = rdir/'apod4.fits'
        specTime = '2000-01-01T00:00:00'

        clim = None
        camLatLon = (40,-80) #not true, just a guess
        x,y,ra,dec,az,el,timeFrame =  fits2azel(fitsfn,camLatLon,specTime,makeplot, clim)

        assert_allclose(ra[[32,51,98],[28,92,156]],[ 152.313342,  157.988921,  165.012208])
        assert_allclose(dec[[32,51,98],[28,92,156]],[ 59.982123,  59.182819,  59.149952])
        assert_allclose(az[[32,51,98],[28,92,156]],[ 22.794418,  20.788267,  17.572719])
        assert_allclose(el[[32,51,98],[28,92,156]],[ 17.359846,  15.084063,  13.287209])

if __name__ == '__main__':
    unittest.main()
