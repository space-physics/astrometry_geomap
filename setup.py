#!/usr/bin/env python3
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--yes','--file','requirements.txt'])
except (Exception,KeyboardInterrupt) as e:
    pass

with open('README.rst','r') as f:
	long_description = f.read()

setup(name='astrometry_azel',
	  description='Uses Astrometry.net program to generate per-pixel azimuth/elevation plate scaling',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/astrometry_azel',
     install_requires=['pymap3d',
                       'pathlib2'],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',],
    extras_require={'pyfits':'pyfits'},
	  )

