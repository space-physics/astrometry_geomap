#!/usr/bin/env python
from setuptools import setup

req = ['pymap3d',
        'nose','python-dateutil','pytz','numpy','scipy','h5py','astropy','scikit-image','matplotlib','seaborn' ]

setup(name='astrometry_azel',
      packages=['astrometry_azel'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/astrometry_azel',
      install_requires=req,
      extras_require={'pyfits':'pyfits'},
	  )

