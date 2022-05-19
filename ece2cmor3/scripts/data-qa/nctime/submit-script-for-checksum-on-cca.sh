#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# Run checksum on the cmorised data.
#
# This scripts requires one arguments:
#  1st argument: the directory path with the cmorised data
#  2nd argument: the experiment ID

# input_dir_name  is the directory with the raw ec-earth output results, for instance: CMIP6

if [ "$#" -eq 2 ]; then

 wall_clock_time=2:00:00    # Maximum estimated time of run, e.g: 6:01:00  means 6 ours, 1 minute, zero seconds
 cores_per_node=18          # The number of cores used per node, recommended at cca is to use one thread, i.e 18 cores per node

 input_dir_name=${1}
 EXP=${2}

 # The directoy where the submit scripts will be launched by qsub:
 running_directory=${PERM}/cmorize/ece2cmor3/ece2cmor3/scripts/data-qa/nctime/



 #===============================================================================
 # Below this line the normal end user doesn't have to change anything
 #===============================================================================


 pbs_header='
#PBS -N checksum-'${EXP}'
#PBS -q nf
#PBS -j oe
#PBS -o pbs-log-for-checksum-'${EXP}'.out
#PBS -l walltime='${wall_clock_time}'
#PBS -l EC_hyperthreads=1
#PBS -l EC_total_tasks=1
#PBS -l EC_threads_per_task='${cores_per_node}'
##PBS -l EC_billing_account=${EC_billing_account}
##PBS -W depend=afterok:<JOB_ID_OF_PREVIOUS_DEPENDENCY_JOB>
'

 # This block of variables need to be checked and adjusted:
 definition_of_script_variables='
 EXP='${EXP}'
 input_dir_name='${input_dir_name}'
 running_directory='${running_directory}'
 '

 job_name=run-checksum-${EXP}.sh

 add_comment='# Run the sha256 checksum on the cmorised data set of the entire experiment:'

 change_dir='cd ${running_directory}'

 checksum_call='
 if [ ${input_dir_name:(-1)} == '/' ]; then
  input_dir_name=${input_dir_name:0:(-1)}
 fi

 file_list=file-overview-${input_dir_name##*/}.txt
 checksum_file=sha256sum-checksum-${input_dir_name##*/}.txt

 cd ${input_dir_name}/../

 # Creating the file overview:
 find ${input_dir_name##*/} -type f > ${file_list}

 # Creating sha256sum checksum:
 /usr/bin/time -f "\t%E real,\t%U user,\t%S sys" -o time-${input_dir_name##*/}.txt -a parallel -k -j 28 -a ${file_list} sha256sum > ${checksum_file}
 '
 one_line_command=$(echo ${checksum_call} | sed -e 's/\\//g')

 check_data_directory='
 if [ ! -d "$input_dir_name"       ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $input_dir_name " does not exist. Aborting job: " $0 >&2; exit 1; fi
 if [ ! "$(ls -A $input_dir_name)" ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $input_dir_name " is empty. Aborting job:" $0 >&2; exit 1; fi
 '

 check_whether_ece2cmor_is_activated='
 if ! type ece2cmor > /dev/null; then echo -e "\e[1;31m Error:\e[0m"" ece2cmor is not activated." ;fi
 '

if [ -d ${PERM}/cmorize/ece2cmor3/ ]; then
 ece2cmor_version_log='
 cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version;                                           cd '${running_directory}';
#cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no           cd '${running_directory}';
#cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no; git diff cd '${running_directory}';
 '
else
 ece2cmor_version_log='
 echo; echo "Using version:"; ece2cmor --version
 '
fi

 # Creating the job submit script which will be submitted by qsub:

 echo "#!/usr/bin/env bash                                                                         " | sed 's/\s*$//g' >  ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " ${pbs_header}                                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " source $SCRATCH/mamba/etc/profile.d/conda.sh                                               " | sed 's/\s*$//g' >> ${job_name}
 echo " conda activate ece2cmor3                                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " export HDF5_USE_FILE_LOCKING=FALSE                                                         " | sed 's/\s*$//g' >> ${job_name}
 echo " export UVCDAT_ANONYMOUS_LOG=false                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_whether_ece2cmor_is_activated}                                                     " | sed 's/\s*$//g' >> ${job_name}
 echo " ${ece2cmor_version_log}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " ${definition_of_script_variables}                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_data_directory}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo 'The ${job_name} job will run:'                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo ${one_line_command}                                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " ${add_comment}                                                                             " | sed 's/\s*$//g' >> ${job_name}
 echo " ${change_dir}                                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo " ${checksum_call}                                                                           " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo 'The ${job_name} job has finished.'                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}

 chmod uog+x ${job_name}


 cd ${running_directory}

 # Submitting the job with qsub:
 qsub ${job_name}

 # Printing some status info of the job:
 echo
 echo ' The ' ${running_directory}${job_name} ' submit script is created and submitted. Monitor your job by:'
 echo '  qstat -u ' ${USER}
 echo '  cd '${running_directory}
 echo

 else
  echo
  echo ' Illegal number of arguments. Needs otwo arguments:'
  echo '  ' $0 /scratch/ms/nl/nklm/cmorisation/cmorised-results/cmor-VAREX-cmip-h015/h015/CMIP6 h015
  echo
 fi
