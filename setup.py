#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])
    

setup(name='astrometry_azel',
      packages=['astrometry_azel'],
      install_requires=['pymap3d',],
      dependency_links = ['https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',],
      extras_require={'pyfits':'pyfits'},
	  )

