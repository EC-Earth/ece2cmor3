#!/usr/bin/env bash
#SBATCH -A optimesm
#SBATCH -t 2:0:0

# submit as sbatch -A 252-451 launch_knmi.sh

module purge
module load Mambaforge/23.3.1-1-hpc1
mamba activate /home/sm_wyser/cmorize/ece2cmor3/.conda

set -ue

tmpdir=$SNIC_TMP

e="x621"
s="ssp126"

m="nemo"

odir=/nobackup/rossby27/proj/optimesm/cmorized_knmi
mkdir -p $odir

sed -e '/"experiment_id":/ c\    "experiment_id":                "'${s}'",
' ~/optimesm/sm_wyser/ece3-optimesm6/runtime/classic/ctrl/output-control-files/cmip6/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp245/metadata-cmip6-ScenarioMIP-ssp245-EC-EARTH-Veg-nemo-template.json $tmpdir/metadata.json

idir=/nobackup/rossby21/rossby/joint_exp/crescendo/ece-run/$e/output/$m/$(printf %03d $SLURM_ARRAY_TASK_ID)

vlist====

time ece2cmor --exp $e --meta $tmpdir/metadata.json --varlist $vlist --$m --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir --skip_alevel_vars $idir
