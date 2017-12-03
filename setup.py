#!/usr/bin/env python
install_requires = ['pillow','python-dateutil','pytz','numpy', 'scipy','h5py', 'astropy','scikit-image',
       'tifffile',
       'pymap3d']
tests_require=['nose','coveralls']
# %%
from setuptools import setup,find_packages

setup(name='astrometry_azel',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      description='Register images to az/el using the astrometry.net program',
      url='https://github.com/scivision/astrometry_azel',
      version='1.1.1',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
      ],
      install_requires=install_requires,
      python_requires='>=3.6',
      tests_require=tests_require,
      extras_require={'tests':tests_require,
                      'plot':['matplotlib','seaborn',]},
	  )

