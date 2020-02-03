#!/bin/bash
# Thomas Reerink
#
# Run this script by:
#  submit-at-cca-ece2cmor-leg-job.sh ifs 001
#
# Cmorise per model component the EC-Earth3 raw output with ece2cmor3 for one leg
#
# This scripts requires two arguments:
#  1st argument: model component
#  2nd argument: leg

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

#PERM=/perm/ms/nl/nktr      # For testing outside cca

 wall_clock_time=0:30:00    # Maximum estimated time of run, e.g: 6:01:00  means 6 ours, 1 minute, zero seconds
 cores_per_node=18          # The number of cores used per node, recommended at cca is to use one thread, i.e 18 cores per node

 COMPONENT=$1
 LEG=$2

 EXP=onep
 ECEDIR=/scratch/ms/nl/nm6/ECEARTH-RUNS/$EXP/output/$COMPONENT/$LEG
 ECEMODEL=EC-EARTH-AOGCM
 METADATA=/perm/ms/nl/nktr/ec-earth-3/trunk/runtime/classic/ctrl/cmip6-output-control-files/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/metadata-cmip6-CMIP-piControl-EC-EARTH-AOGCM-$COMPONENT-template.json
 TEMPDIR=/scratch/ms/nl/nktr/cmorisation/temp-cmor-dir/$EXP/$COMPONENT/$LEG
 VARLIST=/perm/ms/nl/nktr/ec-earth-3/trunk/runtime/classic/ctrl/cmip6-output-control-files/test-all-ece-mip-variables/ece-cmip6-data-request-varlist-all-EC-EARTH-AOGCM.json
 ODIR=/scratch/ms/nl/nktr/cmorisation/cmorised-results/cmor-aerchem-cmip/$EXP/$COMPONENT/$LEG


 #===============================================================================
 # Below this line the normal end user doesn not have to change anything
 #===============================================================================

 pbs_header='
#PBS -N cmor-'${COMPONENT}'-'${LEG}'-'${EXP}'
#PBS -q nf
#PBS -j oe
#PBS -o cmor-'${EXP}'-'${COMPONENT}'-'${LEG}'.out
#PBS -l walltime='${wall_clock_time}'
#PBS -l EC_hyperthreads=1
#PBS -l EC_total_tasks=1
#PBS -l EC_threads_per_task='${cores_per_node}'
'

 # This block of variables need to be checked and adjusted:
 definition_of_script_variables='
 COMPONENT='${COMPONENT}'
 LEG='${LEG}'

 EXP='${EXP}'
 ECEDIR='${ECEDIR}'
 ECEMODEL='${ECEMODEL}'
 METADATA='${METADATA}'
 TEMPDIR='${TEMPDIR}'
 VARLIST='${VARLIST}'
 ODIR='${ODIR}'
 '

 running_directory=/scratch/ms/nl/nktr/cmorisation/
#running_directory='$SCRATCH'/cmorisation/

 job_name=cmorise-${EXP}-$1-$2.sh

 ece2cmor_call='
 ece2cmor $ECEDIR --exp               $EXP      \
                  --ececonf           $ECEMODEL \
                  --$COMPONENT                  \
                  --meta              $METADATA \
                  --varlist           $VARLIST  \
                  --tmpdir            $TEMPDIR  \
                  --odir              $ODIR     \
                  --npp               18        \
                  --overwritemode     replace   \
                  --skip_alevel_vars            \
                  --log
 '
 one_line_command=$(echo ${ece2cmor_call} | sed -e 's/\\//g')
#echo ' ' ${one_line_command}

 check_data_directory='
 if [ ! -d "$ECEDIR"       ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $ECEDIR " does not exist. Aborting job: " $0 >&2; exit 1; fi
 if [ ! "$(ls -A $ECEDIR)" ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $ECEDIR " is empty. Aborting job:" $0 >&2; exit 1; fi
 '

 create_temp_and_output_directories='
 mkdir -p $ODIR
 if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi
 mkdir -p $TEMPDIR
 '

 check_whether_ece2cmor_is_activated='
 if ! type ece2cmor > /dev/null; then echo -e "\e[1;31m Error:\e[0m"" ece2cmor is not activated." ;fi
 '

 ece2cmor_version_log='
#git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version
#git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no
#git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no; git diff
 '

 move_log_files='
 mkdir -p $ODIR/logs
 mv -f $EXP-$COMPONENT-$LEG-*.log $ODIR/logs/
 '

 remove_temp_directory='
#if [ -d $TEMPDIR ]; then rm -rf $TEMPDIR; fi
 '

 # Creating the job submit script which will be submitted by qsub:

 echo "#! /bin/bash                                                                                " | sed 's/\s*$//g' >  ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " ${pbs_header}                                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " source $PERM/miniconda2/etc/profile.d/conda.sh                                             " | sed 's/\s*$//g' >> ${job_name}
 echo " conda activate ece2cmor3                                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " export UVCDAT_ANONYMOUS_LOG=false                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_whether_ece2cmor_is_activated}                                                     " | sed 's/\s*$//g' >> ${job_name}
 echo " ${ece2cmor_version_log}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " ${definition_of_script_variables}                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_data_directory}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " ${create_temp_and_output_directories}                                                      " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " ${ece2cmor_call}                                                                           " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " ${move_log_files}                                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${remove_temp_directory}                                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo ' ${job_name} finished.'                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}

 chmod uog+x ${job_name}

 
 mkdir -p ${running_directory}
 if [ ! -d ${running_directory} ]; then echo; echo -e "\e[1;31m Error:\e[0m"" the directory " '${running_directory}' " does not exist."; echo; exit 1;  fi
 mv -f ${job_name} ${running_directory}
 cd ${running_directory}

 echo
 echo ' The ' ${job_name} ' submit script is created.'
 echo


 # Submitting the job with qsub:
 qsub ${job_name}

 # Printing some status info of the job and the used node:
 echo
 echo ' Using 1 thread with' ${cores_per_node} 'cores at 1 node which has 36 cores.'
 echo
 qstat -u ${USER}
 echo 'qstat -u ' ${USER}
 echo 'cd '${running_directory}
 echo


 else
  echo
  echo '  Illegal number of arguments: the script requires two arguments:'
  echo '   1st argument: model component'
  echo '   2nd argument: leg'
  echo '  For instance:'
  echo '   ' $0 ' nemo 001'
  echo '  Or use:'
  echo '   for i in {nemo,ifs}; do for j in {001..008}; do echo ' $0 ' $i $j; done; done'
  echo '   for i in {nemo,ifs}; do for j in {001..008}; do      ' $0 ' $i $j; done; done'
  echo '   for j in {001..015}; do' $0 ' ifs  $j; done'
  echo '   for j in {001..015}; do' $0 ' nemo $j; done'
  echo
 fi
