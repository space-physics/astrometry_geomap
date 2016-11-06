.. image:: https://zenodo.org/badge/19366614.svg
   :target: https://zenodo.org/badge/latestdoi/19366614
   
.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org/
.. image:: https://travis-ci.org/scienceopen/astrometry_azel.svg?branch=master
    :target: https://travis-ci.org/scienceopen/astrometry_azel
.. image:: https://coveralls.io/repos/scienceopen/astrometry/badge.svg?branch=master&service=github 
   :target: https://coveralls.io/github/scienceopen/astrometry?branch=master

================================================================================================
Azimuth/Elevation converter for `Astrometry.net <https://github.com/dstndstn/astrometry.net>`_
================================================================================================

.. contents::

Note: If you want to work with the intermediate steps (source extraction) or photometry, `see my AstroPy-based examples <https://github.com/scienceopen/starscale>`_.

Prerequisites
=============
`Astrometry.net 0.46 <https://scivision.co/setting-up-astrometry-net-program/>`_ or newer 

or, use the `astrometry.net cloud service--handy for Windows users <http://nova.astrometry.net/upload>`_ 

Installation
============
::

  python setup.py develop

Astrometry.net index files
--------------------------
If you use astrometry.net on your PC, you may need to install the index files and setup your config file to point at them::

  sudo ./setup_data.sh


Command line options
=====================
--h5         write az/el et al to HDF5
--mat        write az/el et al to .mat Matlab save file
--png        write az/el et al to PNG
-h           to see all the options you can use

Examples
=========

Astrometry.net installed on your PC:
------------------------------------
::

  python PlateScaleFITS.py myimg.fits -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --h5 --png

gives HDF5 .h5 with az/el ra/dec and PNG plots of the data. Both files contain the same data, just
for your convenience.

The 61.2 -149.9 is your WGS84 coordinates, 2013-04-02T12:03:23Z is UTC time of the picture.

wcs.fits from the Astrometry.net WEBSITE:
------------------------------------------
first rename wcs.fits to myimg.wcs::

  python PlateScaleFITS.py myimg.wcs -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --h5 --png


