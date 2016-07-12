#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass

setup(name='astrometry_azel',
      packages=['astrometry_azel'],
	  description='Uses Astrometry.net program to generate per-pixel azimuth/elevation plate scaling',
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/astrometry_azel',
      install_requires=['pymap3d',
                       'pathlib2'],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',],
      extras_require={'pyfits':'pyfits'},
	  )

