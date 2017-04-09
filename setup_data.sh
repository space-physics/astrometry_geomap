#!/bin/bash
# this copies the necessary star data (one-time) to your PC
# https://www.scivision.co/setting-up-astrometry-net-program

(
cd ~/astrometry.net/data

for i in {08..19}; do
    wget -nc -nd http://broiler.astrometry.net/~dstn/4200/index-42"$i".fits
done
)

