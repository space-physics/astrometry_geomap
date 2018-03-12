#!/usr/bin/env python
install_requires = ['python-dateutil','pytz','numpy', 'scipy', 'astropy','scikit-image','imageio','h5py',
       'pymap3d']
tests_require=['pytest','nose','coveralls']
# %%
from setuptools import setup,find_packages

setup(name='astrometry_azel',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      description='Register images to az/el using the astrometry.net program',
      long_description=open('README.rst').read(),
      url='https://github.com/scivision/astrometry_azel',
      version='1.1.3',
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      ],
      install_requires=install_requires,
      python_requires='>=3.6',
      tests_require=tests_require,
      extras_require={'tests':tests_require,
                      'plot':['matplotlib','seaborn',],},
	  )

