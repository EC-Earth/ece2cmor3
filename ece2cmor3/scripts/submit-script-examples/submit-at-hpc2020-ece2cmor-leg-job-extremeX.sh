#!/usr/bin/env bash
#
# Run this script without arguments for examples how to call this script.
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for multipe legs
#
#SBATCH --time=01:25:00
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

 # Submitdir for ensemble runs s001-s100: /perm/rufl/ecearth3.3.1_SM/AISF_EN/classic
 # Prior submit script for cmorisation: /perm/rufl/cmorize/extremeX/scripts/submit_leg_cmorization_6hr.sh

 # Data description of raw ECE of entire 100-member ensemble where each enseble has 8 legs (2009-2016):
 #  /scratch/rufl/ecearth3/s001/output/ifs/001
 #                                         ...
 #  /scratch/rufl/ecearth3/s001/output/ifs/008
 #                          ...               
 #                          ...               
 #  /scratch/rufl/ecearth3/s100/output/ifs/001
 #                                         ...
 #  /scratch/rufl/ecearth3/s100/output/ifs/008

 if [ "$#" -eq 3 ]; then

   COMPONENT=$1
   EXPNR=$2
   LEG=$3
   EXP=s$EXPNR
   MEMBER=$s$((10#$EXPNR))

   ECEDIR=/scratch/rufl/ecearth3/$EXP/output/$COMPONENT/$LEG
   ECEMODEL=EC-EARTH-AOGCM
   METADATAbase=${PWD}/../../resources/metadata-templates/extremeX-AISE-metadata-template.json
  #METADATAbase=${PWD}/../../resources/metadata-templates/extremeX-AISC-metadata-template.json
   mkdir -p metadata-files
   METADATA=metadata-files/metadata-extremeX-AISE-$COMPONENT-$EXP-$MEMBER-$LEG.json
  #METADATA=metadata-files/metadata-extremeX-AISC-$COMPONENT-$EXP-$MEMBER-$LEG.json
   sed -e 's/"realization_index":            "1"/"realization_index":            "'$MEMBER'"/' $METADATAbase > $METADATA
   sed -i 's/"sub_experiment_id":            "s001"/"sub_experiment_id":            "'$EXP'"/'                 $METADATA
   TEMPDIR=${SCRATCH}/temp-cmor-dir/extremeX/$EXP/$COMPONENT/$LEG
   VARLIST=${PWD}/../../resources/miscellaneous-data-requests/extremeX/datarequest-extremeX-full-varlist.json
   ODIR=${SCRATCH}/cmorised-results/extremeX

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
                    --skip_alevel_vars            \
                    --log

   mkdir -p $ODIR/logs
   mv -f $EXP-$COMPONENT-$LEG-*.log $ODIR/logs/
  #if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi

 else
  echo
  echo " Illegal number of arguments: the script requires three arguments:"
  echo "  1st argument: model component"
  echo "  2nd argument: member"
  echo "  3rd argument: leg"
  echo " For instance:"
  echo "  sbatch $0 ifs 001 s001 1"
  echo " Or use:"
  echo "  for member in {001..010}; do for leg in {001..008}; do echo sbatch --job-name=cmorise-ifs-\${member}-\${leg} $0 ifs \${member} \${leg}; done; done"
  echo

 fi
