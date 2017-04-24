#!/usr/bin/env python
req = ['nose','pillow','python-dateutil','pytz','numpy','scipy','h5py','astropy','scikit-image','matplotlib','seaborn']
pipreq = ['pymap3d',]
# %%
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] +req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='astrometry_azel',
      packages=['astrometry_azel'],
      author='Michael Hirsch, Ph.D.',
      description='Register images to az/el using the astrometry.net program',
      url='https://github.com/scivision/astrometry_azel',
      version='1.1.1',
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

