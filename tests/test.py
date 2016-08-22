#!/usr/bin/env python
from astrometry_azel import Path
from numpy.testing import assert_allclose,run_module_suite
#
from astrometry_azel import fits2azel

rdir = Path(__file__).parent

def test_fits2azel(makeplot=['skipsolve']):
    fitsfn = rdir/'apod4.fits'
    specTime = '2000-01-01T00:00:00'

    clim = None
    camLatLon = (40,-80) #not true, just a guess
    x,y,ra,dec,az,el,timeFrame =  fits2azel(fitsfn,camLatLon,specTime,makeplot, clim)

    assert_allclose(ra[[32,51,98],[28,92,156]],[ 189.89588992,192.16218762,190.59130435])
    assert_allclose(dec[[32,51,98],[28,92,156]],[ 75.2988419 ,  72.24140773,  68.56344283])
    assert_allclose(az[[32,51,98],[28,92,156]],[ 2.82080627,  2.57013009,  3.60855397])
    assert_allclose(el[[32,51,98],[28,92,156]],[ 25.48537912,  22.37206915,  18.78636572])

if __name__ == '__main__':
    run_module_suite()
