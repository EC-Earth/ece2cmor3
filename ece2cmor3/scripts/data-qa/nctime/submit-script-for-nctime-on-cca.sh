#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# Run nctime on the cmorised data.
#
# This scripts requires two arguments:
#  1st argument: the directory path with the cmorised data
#  2nd argument: the experiment ID

# cmorised_data_dir  is the directory with the raw ec-earth output results, for instance: CMIP6

if [ "$#" -eq 2 ]; then

 wall_clock_time=2:00:00    # Maximum estimated time of run, e.g: 6:01:00  means 6 ours, 1 minute, zero seconds
 cores_per_node=18          # The number of cores used per node, recommended at cca is to use one thread, i.e 18 cores per node

 cmorised_data_dir=${1}
 EXP=${2}

 # The directoy where the submit scripts will be launched by qsub:
 nctime_dir=${PERM}/cmorize/ece2cmor3/ece2cmor3/scripts/data-qa/nctime/
 path_log_subdir=${nctime_dir}/log-nctcck/${EXP}



 #===============================================================================
 # Below this line the normal end user doesn't have to change anything
 #===============================================================================


 pbs_header='
#PBS -N nctime-'${EXP}'
#PBS -q nf
#PBS -j oe
#PBS -o pbs-log-for-nctime-'${EXP}'.out
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
 cmorised_data_dir='${cmorised_data_dir}'
 nctime_dir='${nctime_dir}'
 path_log_subdir='${path_log_subdir}'
 '

 job_name=run-nctime-${EXP}.sh

 add_comment_part_1='Run nctime on the cmorised data set of the entire experiment'
 add_comment_part_2='by checking with the nctime command nctcck the conitinuity of the produced time records:'

 change_dir='cd ${nctime_dir}'
 create_dir='mkdir -p ${path_log_subdir}'

 nctxck_call='nctxck --max-processes -1 -i ${nctime_dir}/esgini-dir -l ${path_log_subdir} ${cmorised_data_dir}'
 nctcck_call='nctcck --max-processes -1 -i ${nctime_dir}/esgini-dir -l ${path_log_subdir} ${cmorised_data_dir}'
 one_line_command_01=$(echo ${nctxck_call} | sed -e 's/\\//g')
 one_line_command_02=$(echo ${nctcck_call} | sed -e 's/\\//g')

 check_data_directory='
 if [ ! -d "$cmorised_data_dir"       ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $cmorised_data_dir " does not exist. Aborting job: " $0 >&2; exit 1; fi
 if [ ! "$(ls -A $cmorised_data_dir)" ]; then echo -e "\e[1;31m Error:\e[0m"" EC-Earth3 data output directory: " $cmorised_data_dir " is empty. Aborting job:" $0 >&2; exit 1; fi
 '

 check_whether_ece2cmor_is_activated='
 if ! type ece2cmor > /dev/null; then echo -e "\e[1;31m Error:\e[0m"" ece2cmor is not activated." ;fi
 '

if [ -d ${PERM}/cmorize/ece2cmor3/ ]; then
 ece2cmor_version_log='
 cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version;                                           cd '${nctime_dir}';
#cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no           cd '${nctime_dir}';
#cd ${PERM}/cmorize/ece2cmor3/; echo; git log |head -n 1 | sed -e "s/^/Using /" -e "s/$/ for/"; ece2cmor --version; git status --untracked-files=no; git diff cd '${nctime_dir}';
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
 echo " source ${SCRATCH}/mamba/etc/profile.d/conda.sh                                             " | sed 's/\s*$//g' >> ${job_name}
 echo " conda activate ece2cmor3                                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " export HDF5_USE_FILE_LOCKING=FALSE                                                         " | sed 's/\s*$//g' >> ${job_name}
 echo " export UVCDAT_ANONYMOUS_LOG=false                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_whether_ece2cmor_is_activated}                                                     " | sed 's/\s*$//g' >> ${job_name}
 echo " ${ece2cmor_version_log}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " ${definition_of_script_variables}                                                          " | sed 's/\s*$//g' >> ${job_name}
 echo " ${check_data_directory}                                                                    " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo 'The ${job_name} job will run:'                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo ${one_line_command_01}                                                                " | sed 's/\s*$//g' >> ${job_name}
 echo " echo ${one_line_command_02}                                                                " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " echo '${add_comment_part_1} ${EXP} ${add_comment_part_2}'                                  " | sed 's/\s*$//g' >> ${job_name}
 echo " ${change_dir}                                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo " ${create_dir}                                                                              " | sed 's/\s*$//g' >> ${job_name}
 echo " ${nctxck_call}                                                                             " | sed 's/\s*$//g' >> ${job_name}
 echo " ${nctcck_call}                                                                             " | sed 's/\s*$//g' >> ${job_name}
 echo "                                                                                            " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}
 echo " echo 'The ${job_name} job has finished.'                                                   " | sed 's/\s*$//g' >> ${job_name}
 echo " echo                                                                                       " | sed 's/\s*$//g' >> ${job_name}

 chmod uog+x ${job_name}


 cd ${nctime_dir}

 # Submitting the job with qsub:
 qsub ${job_name}

 # Printing some status info of the job:
 echo
 echo ' The ' ${nctime_dir}${job_name} ' submit script is created and submitted. Monitor your job by:'
 echo '  qstat -u ' ${USER}
 echo '  cd '${nctime_dir}
 echo

 else
  echo
  echo ' Illegal number of arguments. Needs two arguments, e.g.:'
  echo '  ' $0 ${SCRATCH}/cmorisation/cmorised-results/cmor-lamaclima-FRST/FRST/CMIP6/ FRST
  echo '  ' $0 /scratch/ms/nl/nklm/cmorisation/cmorised-results/cmor-VAREX-cmip-h015/h015/CMIP6 h015
  echo
 fi
