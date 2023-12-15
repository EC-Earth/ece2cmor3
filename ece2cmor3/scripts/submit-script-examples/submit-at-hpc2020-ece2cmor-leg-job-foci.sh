#!/usr/bin/env bash
#
# Run this script without arguments for examples how to call this script.
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for multipe legs
#
#SBATCH --time=00:15:00
#SBATCH --job-name=cmorise
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --qos=np
#SBATCH --output=stdout-cmorisation.%j.out
#SBATCH --error=stderr-cmorisation.%j.out
#SBATCH --account=nlchekli
#SBATCH --mail-type=FAIL

# ECEDIR    is the directory with the raw ec-earth output results, for instance: t001/output/nemo/001
# EXP       is the 4-digit ec-earth experiment ID or label, for instance: t001
# ECEMODEL  is the name of the ec-earth model configuration, for instance: EC-EARTH-AOGCM
# METADATA  is the name of the meta data file, for instance: ece2cmor3/resources/metadata-templates/cmip6-CMIP-piControl-metadata-template.json
# VARLIST   is the name of the variable list, in this case the so called json cmip6 data request file, for instance: cmip6-data-request-varlist-CMIP-piControl-EC-EARTH-AOGCM.json
# TEMPDIR   is the directory where ece2cmor3 is writing files during its execution
# ODIR      is the directory where ece2cmor3 will write the cmorised results of this job
# COMPONENT is the name of the model component for the current job to cmorise
# LEG       is the leg number for the current job to cmorise. Note for instance leg number one is written as 001.

 if [ "$#" -eq 4 ]; then

   COMPONENT=$1
   LEG=$2
   EXP=$3
   VERSION=$4

  #ECEDIR=/ec/res4/scratch/nks/ecearth3/$EXP/output/$COMPONENT/$LEG
  #ECEDIR=/ec/res4/scratch/nktr/ec-earth-3/$EXP/output/$COMPONENT/$LEG
   ECEDIR=${SCRATCH}/ec-earth-3/$EXP/output/$COMPONENT/$LEG
   ECEMODEL=EC-EARTH-AerChem
   METADATA=${PERM}/ec-earth-3/trunk/runtime/classic/ctrl/output-control-files/cmip6/CMIP/EC-EARTH-AerChem/cmip6-experiment-CMIP-amip/metadata-cmip6-CMIP-amip-EC-EARTH-AerChem-$COMPONENT-template.json
   TEMPDIR=${SCRATCH}/temp-cmor-dir/$EXP/$COMPONENT/$LEG
   VARLIST=${PWD}/../../resources/test-data-request/varlist-foci.json
   ODIR=${SCRATCH}/cmorised-results/foci/$EXP/$VERSION

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

   ece2cmor $ECEDIR --exp               $EXP      \
                    --ececonf           $ECEMODEL \
                    --$COMPONENT                  \
                    --meta              $METADATA \
                    --varlist           $VARLIST  \
                    --tmpdir            $TEMPDIR  \
                    --odir              $ODIR     \
                    --npp               28        \
                    --overwritemode     replace   \
                    --refd 1750-01-01 \
                    --tm5par.json       ../foci-tm5par.json \
                    --log
#                   --skip_alevel_vars            \
#                   --tm5par.json       ../foci-tm5par.json \

   mkdir -p $ODIR/logs
   mv -f $EXP-$COMPONENT-$LEG-*.log $ODIR/logs/
   if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi

 else
  echo
  echo " Illegal number of arguments: the script requires four arguments:"
  echo "  1st argument: model component"
  echo "  2nd argument: leg"
  echo "  3rd argument: experiment ID"
  echo "  4th argument: version label"
  echo " For instance:"
  echo "  sbatch $0 ifs 001 t001 v001"
  echo " Or use:"
  echo "  for i in {001..002}; do sbatch --job-name=cmorise-ifs-\$i  $0 ifs  \$i fot2 v001; done"
  echo "  for i in {001..002}; do sbatch --job-name=cmorise-nemo-\$i $0 nemo \$i fot2 v001; done"
  echo "  for i in {001..001}; do sbatch --job-name=cmorise-tm5-\$i  $0 tm5  \$i fot2 v001; done"
  echo
 fi
