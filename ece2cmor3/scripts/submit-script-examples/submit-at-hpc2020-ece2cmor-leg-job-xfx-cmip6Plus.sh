#!/usr/bin/env bash
#
# Run this script without arguments for examples how to call this script.
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for multipe legs
#
#SBATCH --time=00:30:00
#SBATCH --job-name=cmorise
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=5
#SBATCH --qos=nf
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

 if [ "$#" -eq 5 ]; then

   NPP=$1
   COMPONENT=$2
   LEG=$3
   EXP=$4
   VERSION=$5

   ece_branch_root_dir=ecearth3/trunk
   ECEMODEL=EC-EARTH-ESM-1
   MIP_ERA=CMIP6Plus
   MIP=TIPMIP
   EXPERIMENT_NAME=esm-up2p0-gwl2p0

   ECEDIR=${SCRATCH}/${ece_branch_root_dir}/$EXP/output/$COMPONENT/$LEG
   METADATA=${PWD}/../../resources/metadata-templates/cmip6Plus-${MIP}-metadata-$COMPONENT-template.json
   TEMPDIR=${SCRATCH}/temp-cmor-dir/$EXP/$COMPONENT/$LEG
   VARLIST=${PWD}/../../resources/miscellaneous-data-requests/cmip6Plus/time-invariant-request/varlist-APfx-LPfx-OPfx.json
   ODIR=${SCRATCH}/cmorised-results/time-invariant-output/$EXP/$VERSION

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

   ece2cmor $ECEDIR --exp               $EXP                                \
                    --ececonf           $ECEMODEL                           \
                    --$COMPONENT                                            \
                    --meta              $METADATA                           \
                    --varlist           $VARLIST                            \
                    --tabledir          /home/nktr/cmorize/cmip6plus-tables \
                    --tableprefix       MIP                                 \
                    --tmpdir            $TEMPDIR                            \
                    --odir              $ODIR                               \
                    --npp               $NPP                                \
                    --overwritemode     replace                             \
                    --skip_alevel_vars                                      \
                    --log

   if [ "$COMPONENT" = "nemo" ]; then
    # Run the additional sftof.py script, see:
    #  https://github.com/EC-Earth/ece2cmor3/wiki/Recommended-strategies#post-ece2cmor3-production--correction-of-ofx-sftof
    search_path=${ODIR}/${MIP_ERA}/${MIP}/EC-Earth-Consortium/EC-Earth3-ESM-1/${EXPERIMENT_NAME}/r*i*p*f*/OPfx/sftof
    for i in `find ${search_path} -name 'sftof_OPfx*.nc'`; do
     echo
     echo ' Run the Ofx sftof correction:'
     echo "  ../data-qa/scripts/sftof.py ${i}"
     ../data-qa/scripts/sftof.py ${i}
     echo
     echo ' The corrected sftof file:'
     for f in `find ${search_path} -name 'sftof_OPfx*.nc'`; do ls -lrt $f; done
     echo
    done
    for i in `find ${search_path} -name 'sftof_OPfx*.nc.bak'`; do rm -f ${i}; done
   fi

   mkdir -p $ODIR/logs
   mv -f $EXP-$COMPONENT-$LEG-*.log $ODIR/logs/
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
  echo "  sbatch --qos=nf --cpus-per-task=5 --job-name=cmorise-ifs-LPfx  $0 5 ifs  001 t001 v010"
  echo "  sbatch --qos=nf --cpus-per-task=1 --job-name=cmorise-nemo-OPfx $0 1 nemo 001 t001 v010"
  echo
 fi
