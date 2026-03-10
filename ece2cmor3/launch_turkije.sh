#!/usr/bin/env bash
#SBATCH -A optimesm
#SBATCH -t 2:0:0


### sbatch -n 12 -a 165-201%6 -t 40:00 -o logfiles-turkije/t622_%a.out launch_turkije.sh


module purge
module load Mambaforge/23.3.1-1-hpc1
mamba activate /home/sm_wyser/cmorize/ece2cmor3/.conda

set -ue

tmpdir=$SNIC_TMP

e=t624

odir=/nobackup/rossby27/users/sm_wyser/for_turkije/export-4

leg=$((SLURM_ARRAY_TASK_ID+1))
idir=/nobackup/rossby21/rossby/joint_exp/crescendo/ece-run/$e/output/ifs/$(printf %03d $leg)

time ece2cmor --exp $e --meta metadata-turkije.json --varlist varlist-turkije.json --ifs --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir --skip_alevel_vars $idir
