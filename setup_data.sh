#!/bin/bash
# this copies the necessary star data (one-time) to your PC
# unfortunately Astrometry.net does not currently recognize ~ or $HOME for this directory,
# so I thought it more reliable to put it in a commonly accessible directory

mkdir -p /opt/astrometry/data
for i in {08..19}; do
wget -nc -nd -P /opt/astrometry/data http://broiler.astrometry.net/~dstn/4200/index-42"$i".fits
done
