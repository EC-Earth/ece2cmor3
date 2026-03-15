#!/usr/bin/env bash

#SBATCH -N 1 --exclusive
#SBATCH -A optimesm
#SBATCH -t 8:0:0

ml parallel/20220722-hpc1-gcc-2022a-eb
ml Mambaforge/23.3.1-1-hpc1

conda activate ece2cmor3

#set -ue

d=~/optimesm/cmorized/CE42-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1

tmpdir=${SNIC_TMP:-./tmpdir}
mkdir -p $tmpdir

varlist=$tmpdir/varlist
rm -f $varlist

for t in $(ls $d); do
        for v in $(ls $d/$t); do
                echo "$t-$v" >> $varlist
        done
done

time cat varlist | parallel --colsep ' ' ./recmorise-cmip6-to-cmip7.py -t $tmpdir -v {1} {2}
