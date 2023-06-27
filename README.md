
# Azimuth/Elevation converter for [Astrometry.net](https://github.com/dstndstn/astrometry.net)

[![Zenodo DOI](https://zenodo.org/badge/19366614.svg)](https://zenodo.org/badge/latestdoi/19366614)
[![ci](https://github.com/space-physics/astrometry_azel/actions/workflows/ci.yml/badge.svg)](https://github.com/space-physics/astrometry_azel/actions/workflows/ci.yml)
[![PyPi version](https://img.shields.io/pypi/pyversions/astrometry-azel.svg)](https://pypi.python.org/pypi/astrometry-azel)
[![Downloads](http://pepy.tech/badge/astrometry-azel)](http://pepy.tech/project/astrometry-azel)

Note: If you want to work with the intermediate steps (source extraction) or photometry, see my AstroPy-based
[examples](https://github.com/scivision/starscale).

[Tips and techniques article](https://www.scivision.dev/astrometry-tips-techniques), especially for DSLR citizen science data.

## Prerequisites / install

Get
[Astrometry.net &ge; 0.67](https://scivision.dev/astrometry-install-usage)
or use the
[astrometry.net cloud service](http://nova.astrometry.net/upload).

```sh
python3 -m pip install -e .
```

## Command line options

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

### Astrometry.net installed on local computer:

```sh
python3 PlateScale.py myimg.fits -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --nc --png
```

gives NetCDF .nc with az/el ra/dec and PNG plots of the data.
Both files contain the same data, just for your convenience.

61.2 -149.9 is your WGS84 coordinates, 2013-04-02T12:03:23Z is UTC time of the picture.

### wcs.fits from the Astrometry.net website:

```sh
mv wcs.fits myimg.wcs

python3 PlateScale.py -c 61.2 -149.9 -t 2013-04-02T12:03:23Z --nc --png
```

## Notes

* 2MASS [index](http://broiler.astrometry.net/~dstn/4200/)
* Tycho [index](http://broiler.astrometry.net/~dstn/4100/)

* ways to [use astrometry.net](http://astrometry.net/use.html)
* astrometry.net [source code releases](http://astrometry.net/downloads/)
* astrometry.net [GitHub](https://github.com/dstndstn/astrometry.net)

* [article](https://www.dsi.uni-stuttgart.de/institut/mitarbeiter/schindler/Schindler_et_al._2016.pdf) on good robustness of Astrometry.net to shaky, streaked images.

### build astrometry.net

We use Linux or Windows Subsystem for Linux as follows:

wget http://astrometry.net/downloads/astrometry.net-latest.tar.gz
tar xf astrometry.net-latest.tar.gz
cd astrometry*
apt install gcc make libcairo2-dev libnetpbm10-dev netpbm libpng-dev libjpeg-dev python3-numpy python3-pyfits python3-dev zlib1g-dev libbz2-dev swig libcfitsio-dev
make -j
make py -j
make extra -j
make install -j INSTALL_DIR=$HOME/.local/astrometry

add to ~/.bashrc:
```
export PATH=$PATH:$HOME/.local/astrometry/bin
```
open a new terminal to use.

### Download star index files

```sh
python downloadIndex.py
```

Edit file /etc/astrometry.cfg or similar:

Be sure `add_path` points to /home/username/astrometry-data, where username is your Linux username.
Don't use ~ or $HOME.

Uncomment `inparallel` to process much faster.

Optionally, set `minwidth` smaller than the smallest FOV (in degrees) expected.
For example, if NOT using a telescope, perhaps minwidth 1 or something.
