#!/usr/bin/env python
"""
http://nova.astrometry.net/user_images/1572720
"""
import pytest
from pathlib import Path
from pytest import approx

#
from astrometry_azel import fits2azel

rdir = Path(__file__).parent


@pytest.mark.filterwarnings(
    "ignore:The WCS transformation has more axes (2) than the image it is associated with (0)"
)
def test_fits2azel():
    fitsfn = rdir / "apod4.fits"
    time = "2000-01-01T00:00:00"

    camLatLon = (40, -80)  # not true, just a guess
    scale = fits2azel(fitsfn, camLatLon, time)

    assert scale["ra"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [152.313342, 157.988921, 165.012208]
    )
    assert scale["dec"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [59.982123, 59.182819, 59.149952]
    )
    assert scale["az"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [22.794418, 20.788267, 17.572719]
    )
    assert scale["el"].values[[32, 51, 98], [28, 92, 156]] == approx(
        [17.359846, 15.084063, 13.287209]
    )


if __name__ == "__main__":
    pytest.main(["-x", __file__])
