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

# CMIP6
#metadata_tmpl_root=optimesm/metadata-cmip6-CMIP-historical-EC-EARTH-ESM-1

# CMIP6Plus
metadata_tmpl_root=optimesm/metadata-cmip6plus-CMIP-esm-hist-EC-EARTH-ESM-1

case $e in
CD11 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 2000-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "84006.0D",' \
    -e 's/XXXX/SMHI/g' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD12 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-hist",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "7305.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "2",' \
    -e 's/XXXX/SMHI/g' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD31 | CD97 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "182621.0D",' \
    -e 's/XXXX/SMHI/g' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json
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
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
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
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
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
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD45 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "piControl",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl-spinup",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "182621.0D",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl-spinup r1 simulation which is incompatible with current CV",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD44 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "1pctCO2",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "0.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD43 )
  refyear=1850
  sed \
    -e '/"experiment_id"/ c\    "experiment_id":                "abrupt-4xCO2",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "piControl",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "0.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "1",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI. Initial conditions are from the corresponding esm-piControl r1 simulation which is incompatible with current CV",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD63 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "38715.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "5",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD61 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl4p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "75240.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "5",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD73 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl3p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "56613.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD74 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl1p5",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "28854.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD75 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl3p0-50y-dn2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0-gwl3p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "18262.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD76 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl3p0-50y-dn2p0-gwl2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0-gwl3p0-50y-dn2p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "19357.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD78 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl2p0-50y-dn2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0-gwl2p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "18262.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD79 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl4p0-50y-dn2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0-gwl4p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "18262.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
CD80 )
  refyear=1850
  sed \
    -e '/"activity_id"/ c\    "activity_id":                "TIPMIP",' \
    -e '/"experiment_id"/ c\    "experiment_id":                "esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0",' \
    -e '/"parent_activity_id"/ c\    "parent_activity_id":         "TIPMIP",' \
    -e '/"parent_experiment_id"/ c\    "parent_experiment_id":         "esm-up2p0-gwl4p0-50y-dn2p0",' \
    -e '/"parent_variant_label"/ c\    "parent_variant_label":         "r4i1p1f1",' \
    -e '/"parent_time_units"/ c\    "parent_time_units":            "days since 1850-01-01",' \
    -e '/"branch_time_in_parent"/ c\    "branch_time_in_parent":        "35064.0D",' \
    -e '/"realization_index"/ c\    "realization_index":            "4",' \
    -e '/"comment"/ c\    "comment":                      "This experiment was done as part of OptimESM (https://optimesm-he.eu/) by SMHI.",' \
    ${metadata_tmpl_root}-$m-template.json > $tmpdir/metadata.json ;;
esac

#y=$((refyear+SLURM_ARRAY_TASK_ID))
#idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $((y-refyear+1)))

leg=$((SLURM_ARRAY_TASK_ID+1))
idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $leg)

#odir=/nobackup/rossby27/proj/optimesm/cmorized/$(date +%F)
#odir=/nobackup/rossby27/proj/optimesm/cmorized/$e-$((leg/100))
odir=/nobackup/rossby27/proj/optimesm/cmorized/$e

echo "Start processing experiment $e, component $m and leg $leg"

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

##### ???? esac

#y=$((refyear+SLURM_ARRAY_TASK_ID))
#idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $((y-refyear+1)))

leg=$((SLURM_ARRAY_TASK_ID+1))
idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/$e/output/$m/$(printf %03d $leg)

#odir=/nobackup/rossby27/proj/optimesm/cmorized/$(date +%F)
#odir=/nobackup/rossby27/proj/optimesm/cmorized/$e-$((leg/100))
odir=/nobackup/rossby27/proj/optimesm/cmorized/$e

echo "Start processing experiment $e, component $m and leg $leg"

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
vlist=optimesm/optimesm-request-EC-EARTH-ESM-varlist.json
# quick fix
# vlist=varlist-lpjgtables.json

# fix PISCES vars
#vlist=varlist_bad_pisces.json
#odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}_bad_pisces
###odir=${odir}_bad_pisces
#mkdir -p $odir

# fix LPJG yr vars
vlist=varlist_lpjgyr.json
###idir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece-run/${e}_unpacked/output/$m/$(printf %03d $leg)
odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}_lpjgyr
###odir=${odir}_bad_pisces
#mkdir -p $odir



#time ece2cmor --exp $e --meta $tmpdir/metadata.json --varlist $vlist --$m --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir --skip_alevel_vars $idir


# test TIPMIP
vlist=/nobackup/rossby27/proj/optimesm/sm_wyser/ece3-optimesm6/runtime/classic-clean/ctrl/output-control-files/optimesm/optimesm-request-EC-EARTH-ESM-1-varlist-cmip6Plus.json
###vlist=$PWD/optimesm-varlist-reduced.json
###vlist=$PWD/optimesm-varlist-co2.json


tabledir=/nobackup/rossby27/proj/optimesm/sm_wyser/ece2cmor3-testing/ece2cmor3/resources/CMIP6Plus-tables/combined
tableprefix=MIP
odir=/nobackup/rossby27/proj/optimesm/cmorized/${e}-test
mkdir -p $odir


time ece2cmor --exp $e --meta $tmpdir/metadata.json --varlist $vlist --$m --odir $odir --npp $SLURM_CPUS_ON_NODE --tmpdir $tmpdir --skip_alevel_vars --tabledir $tabledir --tableprefix $tableprefix $idir

