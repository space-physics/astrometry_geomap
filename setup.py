#!/usr/bin/env python
from setuptools import setup

req = ['pymap3d',
        'nose','python-dateutil','pytz','numpy','scipy','h5py','astropy','scikit-image','matplotlib','seaborn' ]

setup(name='astrometry_azel',
      packages=['astrometry_azel'],
      author='Michael Hirsch, Ph.D.',
      description='Register images to az/el using the astrometry.net program',
      url='https://github.com/scienceopen/astrometry_azel',
      version='1.0',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      install_requires=req,
      extras_require={'pyfits':'pyfits'},
	  )

