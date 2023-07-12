# build astrometry.net

Usually we don't need to build Astrometry.net.

Linux or Windows Subsystem for Linux:

curl -O http://astrometry.net/downloads/astrometry.net-latest.tar.gz

tar xf astrometry.net-latest.tar.gz

cd astrometry*

apt install gcc make libcairo2-dev libnetpbm10-dev netpbm libpng-dev libjpeg-dev python3-numpy python3-pyfits python3-dev zlib1g-dev libbz2-dev swig libcfitsio-dev

make -j

make py -j

make extra -j

make install -j INSTALL_DIR=$HOME/.local/astrometry

open a new terminal to use.
