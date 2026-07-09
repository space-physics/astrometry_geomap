
# Azimuth/Elevation converter for [Astrometry.net](https://github.com/dstndstn/astrometry.net)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4527817.svg)](https://doi.org/10.5281/zenodo.4527817)
[![ci](https://github.com/space-physics/astrometry_geomap/actions/workflows/ci.yml/badge.svg)](https://github.com/space-physics/astrometry_geomap/actions/workflows/ci.yml)

[Tips and techniques article](https://www.scivision.dev/astrometry-tips-techniques), especially for DSLR citizen science data.

## Installation

The supported operating systems are Linux, macOS, or Windows Subsystem for Linux.
Astrometry.net 0.95 or newer is recommended to have "solve-field --index-dir" option.
This is available with Ubuntu 26.04 or newer, or macOS Homebrew.
For Windows, use Windows Subsystem for Linux with Ubuntu 26.04 or newer.

* Linux: `apt install astrometry.net`
* macOS: `brew install astrometry-net`

Download this source code

```sh
git clone https://github.com/space-physics/astrometry_geomap.git
```

Setup a Python virtual environment and install this package:

```sh
python3 -m venv astromenv
# arbitrary virtual environment name, e.g. astromenv
source astromenv/bin/activate

pip install -e ./astrometry_geomap
```

Finally, the star index files are needed for astrometry.net to work.

```sh
python -m astrometry_azel.download
```

If you wish to run the self-tests, do from the "astrometry_geomap/" directory:

```sh
pytest -sv
```

## Usage

The main program most users would use to register a star field image to Azimuth and Elevation is

```sh
python -m astrometry_azel -h
```

The "--args" command line option allows passing through a variety of parameters to `solve-field`, which underlies this program.
Type `solve-field -h` or `man solve-field` for a brief description of the nearly 100 options available.

Be sure to enclose the options in quotes.
For example, to specify that the image field is at least 20 degrees in extent:

```sh
python -m astrometry_azel ~/data/myimg.jpg --args "--scale-low 20"
```

Citizen science images often contain extraneous items in the image field of view.
These can very easily break `solve-field`, which is designed for professional science-grade imagery from telescopes and narrow to medium field of view imagers (at least to 50 degree FOV).
To mitigate these issues, judicious use of arguments passed to `solve-field` via `--args` is probably a good start.

The parameters I find most useful for citizen science images include:

```
--scale-low <scale>: lower bound of image scale estimate

--scale-high <scale>: upper bound of image scale estimate

--depth <number or range>: number of field objects to look at, or range
          of numbers; 1 is the brightest star, so "-d 10" or "-d 1-10" mean look
          at the top ten brightest stars only.
```

For extraneous regions of the image, try making a copy of the original image that has the offending regions  cropped out.
If the original image is in a lossy format such as JPEG, consider saving in a lossless format such as PNG after cropping.

### Astrometry.net installed on local computer

```sh
python -m astrometry_azel myimg.fits 61.2 -149.9 2013-04-02T12:03:23Z
```

gives netCDF .nc with az/el ra/dec and PNG plots of the data.
Both files contain the same data, just for your convenience.

61.2 -149.9 is your WGS84 coordinates, 2013-04-02T12:03:23Z is UTC time of the picture.

### wcs.fits from the Astrometry.net website

Download from nova.astrometry.net solved image the "new-image.fits" and "wcs.fits" files, then:

```sh
python -m astrometry_azel 61.2 -149.9 2013-04-02T12:03:23Z new-image.fits
```

## Notes

* 2MASS [index](https://data.astrometry.net/4200/)
* Tycho [index](https://data.astrometry.net/4100/)

* ways to [use astrometry.net](https://astrometry.net/use.html)
* astrometry.net [source code releases](https://astrometry.net/downloads/)
* astrometry.net [GitHub](https://github.com/dstndstn/astrometry.net)

* [article](https://www.dsi.uni-stuttgart.de/institut/mitarbeiter/schindler/Schindler_et_al._2016.pdf) on good robustness of Astrometry.net to shaky, streaked images.

### Download star index files

```sh
python downloadIndex.py
```

Edit file "/etc/astrometry.cfg" or similar:

Be sure `add_path` points to /home/username/astrometry-data, where username is your Linux username.
Don't use ~ or $HOME.

Uncomment `inparallel` to process much faster.

Optionally, set `minwidth` smaller than the smallest FOV (in degrees) expected.
For example, if NOT using a telescope, perhaps minwidth 1 or something.

## PlotGeomap.py

Plot an image registered to Latitude and Longitude, assuming the image features all occurred at a single altitude.
This technique is used in aeronomy assuming a certain altitude of auroral or airglow emissions.
This approximation is based on colors representing particle dynamics at a range of altitudes, approximated by a single altitude.
For example, if a short wavelength filter (blue) was applied to the auroral image, one might assume the emissions were at about 100 km altitude.

## Related

For source extraction or photometry, see my AstroPy-based
[examples](https://github.com/scivision/starscale).
