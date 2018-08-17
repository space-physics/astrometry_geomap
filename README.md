[![Zenodo DOI](https://zenodo.org/badge/19366614.svg)](https://zenodo.org/badge/latestdoi/19366614)
[![AstroPy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)
[![Xarray](https://img.shields.io/badge/powered%20by-xarray-orange.svg?style=flat)](http://xarray.pydata.org/en/stable/why-xarray.html)
[![Travis-CI](https://travis-ci.org/scivision/astrometry_azel.svg?branch=master)](https://travis-ci.org/scivision/astrometry_azel)
[![Coverage](https://coveralls.io/repos/github/scivision/astrometry_azel/badge.svg?branch=master)](https://coveralls.io/github/scivision/astrometry_azel?branch=master)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/0hfbtk1om99mfy0o?svg=true)](https://ci.appveyor.com/project/scivision/astrometry-azel)
[![PyPi version](https://img.shields.io/pypi/pyversions/astrometry-azel.svg)](https://pypi.python.org/pypi/astrometry-azel)
[![PyPi formats](https://img.shields.io/pypi/format/astrometry-azel.svg)](https://pypi.python.org/pypi/astrometry-azel)
[![Downloads](http://pepy.tech/badge/astrometry-azel)](http://pepy.tech/project/astrometry-azel)

# Azimuth/Elevation converter for [Astrometry.net](https://github.com/dstndstn/astrometry.net)

Note: If you want to work with the intermediate steps (source extraction) or photometry, see my AstroPy-based 
[examples](https://github.com/scivision/starscale).

## Prerequisites

[Astrometry.net &ge; 0.67](https://scivision.co/setting-up-astrometry-net-program/)
or, use the 
[astrometry.net cloud service](http://nova.astrometry.net/upload).

## Installation
```sh
python -m pip install -e .
```

### Astrometry.net index files

If you use astrometry.net on your PC, you may need to install the index
files and setup your config file to point at them:
```sh
downloadIndex ~/data
```

## Command line options

### Pass-through arguments

The `-a` `--args` command line option allows passing through a variety of parameters to `solve-field`, which underlies this program.
Type `solve-field -h` or `man solve-field` for a brief description of the nearly 100 options available.

Be sure to enclose the options in quotes. 
For example, to specify that the image field is at least 20 degrees in extent:
```sh
PlateScale ~/data/myimg.jpg -a "-L 20"
```
 

## Examples

Citizen science images often contain extraneous items in the image field of view.
These can very easily break `solve-field`, which is designed for professional science-grade imagery from telescopes and narrow to medium field of view imagers (at least to 50 degree FOV).
To mitigate these issues, judicious use of arguments passed to `solve-field` via `--args` is probably a good start.

The parameters I find most useful for citizen science images include:
```
-L / --scale-low <scale>: lower bound of image scale estimate
-H / --scale-high <scale>: upper bound of image scale estimate
 -d / --depth <number or range>: number of field objects to look at, or range
          of numbers; 1 is the brightest star, so "-d 10" or "-d 1-10" mean look
          at the top ten brightest stars only.
```

For extraneous regions of the image, try making a copy of the original image that has the offending regions cropped out. 
If the original image is in a lossy format such as JPEG, consider saving in a lossless format such as PNG after cropping.

### FITS image input
FITS is a legacy file format commonly used in astronomy.

#### Astrometry.net installed on your PC
```sh
PlateScaleFITS myimg.fits -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --nc --png
```
gives NetCDF .nc with az/el ra/dec and PNG plots of the data. 
Both files contain the same data, just for your convenience.

61.2 -149.9 is your WGS84 coordinates, 2013-04-02T12:03:23Z is UTC time of the picture.

#### wcs.fits from the Astrometry.net WEBSITE

first rename wcs.fits to myimg.wcs:
```sh
PlateScaleFITS myimg.wcs -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --nc --png
```

### JPG image input
JPG is commonly used by prosumer cameras.
It's preferable to use lossless formats for scientific imaging such as JPEG2000 or newer file formats.


## Notes

* 2MASS [index](http://broiler.astrometry.net/~dstn/4200/)
* Tycho [index](http://broiler.astrometry.net/~dstn/4100/)

* ways to [use astrometry.net](http://astrometry.net/use.html)
* astrometry.net [source code releases](http://astrometry.net/downloads/)
* astrometry.net [GitHub](https://github.com/dstndstn/astrometry.net)

* [article](https://www.dsi.uni-stuttgart.de/institut/mitarbeiter/schindler/Schindler_et_al._2016.pdf) on good robustness of Astrometry.net to shaky, streaked images.
