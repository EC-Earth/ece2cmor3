#!/bin/bash

grib_filter_cmd=grib_filter
expname="ECE3"
outputdate=199001
datapath=$SCRATCH/ec-earth
tmppath=/tmp
leg=001

path="$datapath/$expname/output/ifs/$leg"
mkdir -p $tmppath
cp filter6h $tmppath
cd $tmppath
${grib_filter_cmd} filter6h $path/ICMGG$expname+$outputdate &
${grib_filter_cmd} filter6h $path/ICMSH$expname+$outputdate
wait
mkdir -p 3hr
mkdir -p 6hr
mv reduced_gg_3h 3hr/ICMGG$expname+$outputdate
mv reduced_gg_6h 6hr/ICMGG$expname+$outputdate
mv sh_3h 3hr/ICMSH$expname+$outputdate
mv sh_6h 6hr/ICMSH$expname+$outputdate
rm filter6h
cd -
./prim_atm_6hr.py -d $tmppath/6hr -c primavera.json -e $expname -t $tmppath &
./prim_atm_3hr.py -d $tmppath/3hr -c primavera.json -e $expname -t $tmppath 
