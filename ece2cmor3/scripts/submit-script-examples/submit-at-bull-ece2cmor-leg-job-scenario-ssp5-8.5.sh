#!/bin/bash
#
# Run this script by:
#  sbatch submit-at-bull-ece2cmor-leg-job.sh
#  for i in {001..010}; do sbatch submit-at-bull-ece2cmor-leg-job.sh ifs $i; done
#  for i in {nemo,ifs}; do for j in {001..010}; do sbatch submit-at-bull-ece2cmor-leg-job.sh $i $j; done; done
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for multipe legs
#
# This scripts requires two arguments:
#  1st argument: model component
#  2nd argument: leg
#
#SBATCH --job-name=cmorise
#SBATCH --partition=all
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --account=proj-cmip6

# Two account options:  proj-cmip6  &  model-testing

# ECEDIR    is the directory with the raw ec-earth output results, for instance: t001/output/nemo/001
# EXP       is the 4-digit ec-earth experiment ID or label, for instance: t001
# ECEMODEL  is the name of the ec-earth model configuration, for instance: EC-EARTH-AOGCM
# METADATA  is the name of the meta data file, for instance: ece2cmor3/resources/metadata-templates/cmip6-CMIP-piControl-metadata-template.json
# VARLIST   is the name of the variable list, in this case the so called json cmip6 data request file, for instance: cmip6-data-request-varlist-CMIP-piControl-EC-EARTH-AOGCM.json
# TEMPDIR   is the directory where ece2cmor3 is writting files during its execution
# ODIR      is the directory where ece2cmor3 will write the cmorised results of this job
# COMPONENT is the name of the model component for the current job to cmorise
# LEG       is the leg number for the current job to cmorise. Note for instance leg number one is written as 001.

 if [ "$#" -eq 2 ]; then

   COMPONENT=$1
   LEG=$2

   EXP=s585
   ECEDIR=/lustre3/projects/CMIP6/reerink/ec-earth-3/branch-r6874-control-output-files/$EXP/output/$COMPONENT/$LEG
   ECEMODEL=EC-EARTH-AOGCM
   METADATA=/nfs/home/users/reerink/ec-earth-3/trunk/runtime/classic/ctrl/cmip6-output-control-files/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/metadata-cmip6-ScenarioMIP-ssp585-EC-EARTH-AOGCM-$COMPONENT-template.json
   TEMPDIR=/lustre3/projects/CMIP6/reerink/temp-cmor-dir/$EXP/$COMPONENT/$LEG
   VARLIST=/nfs/home/users/reerink/ec-earth-3/trunk/runtime/classic/ctrl/cmip6-output-control-files/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-AOGCM.json
   ODIR=/lustre3/projects/CMIP6/reerink/cmorised-results/cmor-cmip-scenario-ssp5-8.5/$EXP

   if [ -z "$ECEDIR" ]; then echo "Error: Empty EC-Earth3 data output directory: " $ECEDIR ", aborting" $0 >&2; exit 1; fi

   mkdir -p $ODIR
   if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi
   mkdir -p $TEMPDIR

   export PATH="${HOME}/miniconda2/bin:$PATH"
   conda activate ece2cmor3

   export HDF5_USE_FILE_LOCKING=FALSE
   export UVCDAT_ANONYMOUS_LOG=false

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
   if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi

   # Launching the next job for the next leg:
   arg0=$0
   arg1=$1
   arg2previous=$2
   arg2next=$((${arg2previous}+16))  # Note +8 combines with the {nemo,ifs}-for-loop example below to 16 simultaneous jobs
   arg2=$(printf %.3d ${arg2next} )
   if [ ${arg2next} -lt 252 ] ; then
    echo ' A next job is launched:'
    echo ' ' sbatch --job-name=cmorise-${arg1}-${arg2} ${arg0} ${arg1} ${arg2}
    sbatch --job-name=cmorise-${arg1}-${arg2} ${arg0} ${arg1} ${arg2}
   else
    echo ' No next job is launched.'
   fi

 else
  echo
  echo '  Illegal number of arguments: the script requires two arguments:'
  echo '   1st argument: model component'
  echo '   2nd argument: leg'
  echo '  For instance:'
  echo '   sbatch ' $0 ' ifs 001'
  echo '  Or use:'
  echo '   for i in {nemo,ifs}; do for j in {166..173}; do echo sbatch --job-name=cmorise-$i-$j ' $0 ' $i $j; done; done'
  echo '   for i in {nemo,ifs}; do for j in {166..173}; do      sbatch --job-name=cmorise-$i-$j ' $0 ' $i $j; done; done'
  echo '   for j in {166..181}; do sbatch --job-name=cmorise-ifs-$j ' $0 ' ifs $j; done'
  echo '   for j in {166..181}; do sbatch --job-name=cmorise-nemo-$j ' $0 ' nemo $j; done'
  echo
 fi
