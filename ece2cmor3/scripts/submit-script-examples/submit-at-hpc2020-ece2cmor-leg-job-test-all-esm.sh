#!/usr/bin/env bash
#
# Run this script without arguments for examples how to call this script.
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for multipe legs
#
#SBATCH --time=03:05:00
#SBATCH --job-name=cmorise
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --qos=np
#SBATCH --output=stdout-cmorisation.%j.out
#SBATCH --error=stderr-cmorisation.%j.out
#SBATCH --account=nlchekli
#SBATCH --mail-type=FAIL

# ECEDIR    is the directory with the raw ec-earth output results, for instance: t001/output/nemo/001
# EXPID     is the 4-digit ec-earth experiment ID or label, for instance: t001
# ECEMODEL  is the name of the ec-earth model configuration, for instance: EC-EARTH-AOGCM
# METADATA  is the name of the meta data file, for instance: ece2cmor3/resources/metadata-templates/cmip6-CMIP-piControl-metadata-template.json
# VARLIST   is the name of the variable list, in this case the so called json cmip6 data request file, for instance: cmip6-data-request-varlist-CMIP-piControl-EC-EARTH-AOGCM.json
# TEMPDIR   is the directory where ece2cmor3 is writing files during its execution
# ODIR      is the directory where ece2cmor3 will write the cmorised results of this job
# COMPONENT is the name of the model component for the current job to cmorise
# LEG       is the leg number for the current job to cmorise. Note for instance leg number one is written as 001.

 if [ "$#" -eq 5 ]; then

   NPP=$1
   COMPONENT=$2
   LEG=$3
   EXPID=$4
   VERSION=$5

   ece_branch_root_dir=ecearth3/trunk
   ECEMODEL=EC-EARTH-ESM-1
   MIP_ERA=CMIP6
   MIP=CMIP
   EXPERIMENT_NAME=esm-hist

  #TABLEDIR=../../resources/cmip6-cmor-tables/Tables
  #TABLEPREFIX=CMIP6

   ECEDIR=${SCRATCH}/${ece_branch_root_dir}/$EXPID/output/$COMPONENT/$LEG
  #METADATA=${PERM}/${ece_branch_root_dir}/runtime/classic/ctrl/output-control-files/cmip6/$MIP/$ECEMODEL/cmip6-experiment-$MIP-${EXPERIMENT_NAME}/metadata-cmip6-$MIP-${EXPERIMENT_NAME}-$ECEMODEL-$COMPONENT-template.json
   METADATA=${PWD}/../../resources/metadata-templates/metadata-cmip6-$MIP-${EXPERIMENT_NAME}-$ECEMODEL-$COMPONENT-template.json
   TEMPDIR=${SCRATCH}/temp-cmor-dir/$EXPID/$COMPONENT/$LEG
  #VARLIST=${PERM}/ecearth3/trunk/runtime/classic/ctrl/output-control-files/cmip6/test-all-ece-mip-variables/cmip6-data-request-varlist-all-$ECEMODEL.json
   VARLIST=${PWD}/../../resources/miscellaneous-data-requests/test-all/cmip6-data-request-varlist-all-$ECEMODEL.json
  #VARLIST=${PWD}/../../resources/miscellaneous-data-requests/test-data-request/varlist-minimal-test.json
   ODIR=${SCRATCH}/cmorised-results/test-all-trunk/$EXPID/$VERSION

   if [ ! -d "$ECEDIR"       ]; then echo "Error: EC-Earth3 data output directory: $ECEDIR doesn't exist. Aborting job: $0" >&2; exit 1; fi
   if [ ! "$(ls -A $ECEDIR)" ]; then echo "Error: EC-Earth3 data output directory: $ECEDIR is empty.      Aborting job: $0" >&2; exit 1; fi

   mkdir -p $ODIR
   if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi
   mkdir -p $TEMPDIR

   source ${PERM}/mamba/etc/profile.d/conda.sh
   conda activate ece2cmor3

   export HDF5_USE_FILE_LOCKING=FALSE
   export UVCDAT_ANONYMOUS_LOG=false
  #export ECE2CMOR3_IFS_CLEANUP=FALSE

   ece2cmor $ECEDIR --exp               $EXPID       \
                    --ececonf           $ECEMODEL    \
                    --$COMPONENT                     \
                    --meta              $METADATA    \
                    --varlist           $VARLIST     \
                    --tmpdir            $TEMPDIR     \
                    --odir              $ODIR        \
                    --npp               $NPP         \
                    --overwritemode     replace      \
                    --skip_alevel_vars               \
                    --log

   mkdir -p $ODIR/logs
   mv -f $EXPID-$COMPONENT-$LEG-*.log $ODIR/logs/
   if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi

 else
  echo
  echo " Illegal number of arguments: the script requires four arguments:"
  echo "  1st argument: number of processors"
  echo "  2nd argument: model component"
  echo "  3rd argument: leg"
  echo "  4th argument: experiment ID"
  echo "  5th argument: version label"
  echo " For instance:"
  echo "  sbatch --qos=np --cpus-per-task=64 --job-name=cmorise-ifs-001 $0 64 ifs 001 t001 v001"
  echo " Or use:"
  echo "  for i in {001..001}; do sbatch --qos=np --cpus-per-task=64 --job-name=cmorise-ifs-\$i  $0 64 ifs  \$i t001 v001; done"
  echo "  for i in {001..001}; do sbatch --qos=nf --cpus-per-task=1  --job-name=cmorise-nemo-\$i $0  1 nemo \$i t001 v001; done"
  echo "  for i in {001..001}; do sbatch --qos=nf --cpus-per-task=1  --job-name=cmorise-lpjg-\$i $0  1 lpjg \$i t001 v001; done"
  echo "  for i in {001..001}; do sbatch --qos=nf --cpus-per-task=1  --job-name=cmorise-tm5-\$i  $0  1 tm5  \$i t001 v001; done"
  echo
 fi
