#!/usr/bin/env bash
#SBATCH -A optimesm
#SBATCH -t 2:0:0

module purge
module load Mambaforge/23.3.1-1-hpc1
#mamba activate /home/sm_wyser/cmorize/ece2cmor3/.conda
mamba activate ece2cmor3

set -ue

tmpdir=$SNIC_TMP

e=$1
m=$2

case $e in
CD11 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 2000-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "84006.0D",' \
    -e 's/XXXX/SMHI/g' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json ;;
CD12 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-hist",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "7305.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "2",' \
    -e 's/XXXX/SMHI/g' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json ;;
CD31 | CD97 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "182621.0D",' \
    -e 's/XXXX/SMHI/g' \
    optimesm/metadata-cmip6-CMIP-esm-hist-EC-EARTH-ESM-1-$m-template.json > $tmpdir/metadata.json
      ;;
CD37 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-hist",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "29219.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "5",' \
    -e 's/XXXX/SMHI/g' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json ;;
CD46 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "historical",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "29219.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "5",' \
    -e 's/XXXX/SMHI/g' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
CD50 )
  refyear=1979
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "amip",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "no parent",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "no parent",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "no parent",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "no parent",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    -e '/source_type/ c\    "source_type":                  "AGCM",' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
CD45 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "182621.0D",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl-spinup r1 simulation which is incompatible with current CV",' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
CD44 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "1pctCO2",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "0.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
CD43 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "abrupt-4xCO2",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "0.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
CD63 )
  refyear=1850
  sed \
    -e '/"mip_era"/ c\    "mip_era":                "CMIP6Plus",' \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl2p0",' \
    -e '/"parent_mip_era"/ c\    "parent_mip_era":         "CMIP6Plus",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "38715.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "5",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    -e '/"_control_vocabulary_file"/ c\    "_controlled_vocabulary_file":            "CMIP6Plus_CV.json",' \
    -e '/"contact"/ a\,\n\n    "_AXIS_ENTRY_FILE": "MIP_coordinate.json",\n    "_FORMULA_VAR_FILE": "MIP_formula_terms.json"' \
    -e '/"license"/ c\     "license":                      "CMIP6Plus model data produced by EC-Earth-Consortium is licensed under a Creative Commons 4.0 (CC BY 4.0) License (https://creativecommons.org/). Consult https://pcmdi.llnl.gov/CMIP6Plus/TermsOfUse for terms of use governing CMIP6Plus output, including citation requirements and proper acknowledgment. The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law.",'\
    optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-$m-template.json > $tmpdir/metadata.json
      ;;
t607 | t613 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "historical",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "29219.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    /nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm6/runtime/classic/ctrl/output-control-files/cmip6/CMIP/EC-EARTH-Veg/cmip6-experiment-CMIP-historical/metadata-cmip6-CMIP-historical-EC-EARTH-Veg-$m-template.json > $tmpdir/metadata.json
      ;;
t605 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "historical",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "0.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "2",' \
    /nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm6/runtime/classic/ctrl/output-control-files/cmip6/CMIP/EC-EARTH-Veg/cmip6-experiment-CMIP-historical/metadata-cmip6-CMIP-historical-EC-EARTH-Veg-$m-template.json > $tmpdir/metadata.json
      ;;
t608 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "historical",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "18262.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "3",' \
    /nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm6/runtime/classic/ctrl/output-control-files/cmip6/CMIP/EC-EARTH-Veg/cmip6-experiment-CMIP-historical/metadata-cmip6-CMIP-historical-EC-EARTH-Veg-$m-template.json > $tmpdir/metadata.json
      ;;
t624 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "ssp585",' \
    -e '/"activity_id"/ c\    "activity_id":                "ScenarioMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "historical",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "60265.0D",' \
    -e '/"branch_time_in_child"/ c\    "branch_time_in_child":        "60265.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    /nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm6/runtime/classic/ctrl/output-control-files/cmip6/CMIP/EC-EARTH-Veg/cmip6-experiment-CMIP-historical/metadata-cmip6-CMIP-historical-EC-EARTH-Veg-$m-template.json > $tmpdir/metadata.json
      ;;
CE37 | CE38 | CE42 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "182621.0D",' \
    -e 's/XXXX/SMHI/g' \
    /nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm7/runtime/classic/ctrl/output-control-files/optimesm-cmip7-ft-core/metadata-cmip6-CMIP-esm-hist-EC-EARTH-ESM-1-$m-template.json > $tmpdir/metadata.json
      ;;
esac

#y=$((refyear+SLURM_ARRAY_TASK_ID))
#idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $((y-refyear+1)))

leg=$((SLURM_ARRAY_TASK_ID+1))
idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $leg)

#odir=/nobackup/rossby27/proj/optimesm/cmorized/$(date +%F)
#odir=/nobackup/rossby27/proj/optimesm/cmorized/$e-$((leg/100))
odir=/nobackup/rossby27/proj/optimesm/cmorized/$e-$((leg/100))-ext
#odir=/nobackup/rossby27/proj/optimesm/cmorized/$e
mkdir -p $odir

echo "Start processing experiment $e, component $m and $leg"

if [[ $e == 'CD11' ]] && (( leg <= 110 ))
then
	# remove some lpjg variables prior to leg 113 in piControl
	vlist=optimesm/optimesm-request-EC-EARTH-ESM-varlist-$e-before113.json
elif [[ $e == 'CD11' ]] && (( leg <= 120 ))
then
	# remove some lpjg variables prior to leg 120 in piControl
	vlist=optimesm/optimesm-request-EC-EARTH-ESM-varlist-$e-before120.json
elif [[ $e == 'CD11' ]] && (( leg <= 132 ))
then
	# remove some lpjg variables prior to leg 132 in piControl
	vlist=optimesm/optimesm-request-EC-EARTH-ESM-varlist-$e-before132.json
else
	vlist=optimesm/optimesm-request-EC-EARTH-ESM-varlist.json
fi

# after fixing lpj
vlist=optimesm/optimesm-request-EC-EARTH-ESM-1-varlist.json
# quick fix
# vlist=varlist-lpjgtables.json

# fix PISCES vars
#vlist=varlist_bad_pisces.json
#odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}_bad_pisces
###odir=${odir}_bad_pisces
#mkdir -p $odir

# fix LPJG yr vars
#vlist=varlist_lpjgyr.json
###idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/${e}_unpacked/output/$m/$(printf %03d $leg)
#odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}_lpjgyr
#mkdir -p $odir

# for Misha
idir=/nobackup/rossby22/rossby/joint_exp/cmip6/${e}/output/ifs/$(printf %03d $leg)
idir=/nobackup/rossby22/rossby/joint_exp/crescendo/ece-run-recover/$e/output/$m/$(printf %03d $leg)
odir=/nobackup/rossby27/proj/rossby/joint_exp/ecearth/cmorized
vlist=varlist-zg8.json

# for DWD (Frank)
#idir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/$e/output/$m/$(printf %03d $leg)
#odir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/cmorized-frank
#vlist=varlist-zg8.json

# for Jennifer 
#idir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/$e/output/$m/$(printf %03d $leg)
#odir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/cmorized-jennifer
#vlist=varlist-jennifer.json

# for Marco 
idir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/$e/output/$m/$(printf %03d $leg)
odir=/nobackup/accmls1/proj/rossby/users/sm_wyser/cmip6-stuff/cmorized-marco
vlist=varlist-marco.json

# test CMIP7
vlist=/home/sm_wyser/optimesm/sm_wyser/cmip7-drq/output-control-files-ECE3-CMIP7/cmip7/historical-high-EC-Earth3-ESM-1/component-request-cmip7-historical-high-EC-Earth3-ESM-1.json
idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $leg)
odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}-test
mkdir -p $odir

# test-2 CMIP7
case $e in
	CE37 | CE42 ) vlist=/nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm7/runtime/classic/ctrl/output-control-files/optimesm-cmip7-ft-core/combinded-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json ;;
	CE38 ) vlist=/nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm7/runtime/classic/ctrl/output-control-files/optimesm-cmip7-ft-high/combinded-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json ;;
esac

time ece2cmor --exp $e --meta $tmpdir/metadata.json --varlist $vlist --$m --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir --skip_alevel_vars $idir

