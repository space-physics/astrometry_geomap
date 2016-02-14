#!/usr/bin/env python3

from setuptools import setup
import subprocess

with open('README.rst','r') as f:
	long_description = f.read()

setup(name='astrometry_azel',
      version='0.1',
	  description='Uses Astrometry.net program to generate per-pixel azimuth/elevation plate scaling',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/astrometry_azel',
     install_requires=['pymap3d'],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',],
    extras_require={'pyfits':'pyfits'},
      packages=['astrometry_azel'],
	  )

#%%
try:
    subprocess.run(['conda','install','--yes','--quiet','--file','requirements.txt']) #don't use os.environ
except Exception as e:
    print('you will need to install packages in requirements.txt  {}'.format(e))
