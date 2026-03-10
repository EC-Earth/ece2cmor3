#!/usr/bin/env bash
#SBATCH -A optimesm
#SBATCH -t 2:0:0

module purge
module load Mambaforge/23.3.1-1-hpc1
mamba activate /home/sm_wyser/cmorize/ece2cmor3/.conda

set -ue

tmpdir=$SNIC_TMP

e=$1
m=$2

case $e in
	'x621' ) ssp='ssp126' ;;
	'x623' ) ssp='ssp370' ;;
	* ) echo "$e not ready yet, exit" ;;
esac

leg=$((SLURM_ARRAY_TASK_ID+1))
idir=$HOME/crescendo/ece-run/$e/output/$m/$(printf %03d $leg)

odir=/nobackup/rossby27/proj/optimesm/sm_wyser/for_export/for_dwd_$ssp
mkdir -p $odir


time ece2cmor --exp $e --meta metadata-dwd-$ssp-$m.json --varlist varlist-dwd.json --$m --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir $idir
