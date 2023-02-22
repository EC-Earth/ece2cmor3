#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# This scripts needs two arguments
#  first  argument is the directory path of the b2share directory for the ece2cmor git repository
#
# This script downloads all files from the b2share ece2cmor3 dataset. This is part of the ece2cmor3 installation.
#

if [ "$#" -eq 1 ]; then

 b2share_directroy=${1}

 b2share_ece2cmor_dataset_address=https://b2share.eudat.eu/api/files/359aeba7-9416-4896-bf34-6905eb21302e

 b2share_file_01=fx-sftlf-EC-Earth3-T159.nc
 b2share_file_02=fx-sftlf-EC-Earth3-T255.nc
 b2share_file_03=fx-sftlf-EC-Earth3-T511.nc
 b2share_file_04=nemo-vertices-ORCA1-t-grid.nc
 b2share_file_05=nemo-vertices-ORCA1-u-grid.nc
 b2share_file_06=nemo-vertices-ORCA1-v-grid.nc
 b2share_file_07=nemo-vertices-ORCA025-t-grid.nc
 b2share_file_08=nemo-vertices-ORCA025-u-grid.nc
 b2share_file_09=nemo-vertices-ORCA025-v-grid.nc
 b2share_file_10=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-HR.nc
 b2share_file_11=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR.nc
 b2share_file_12=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR-pliocene.nc
 b2share_file_13=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables.nc

 b2share_files=(
  fx-sftlf-EC-Earth3-T159.nc
  fx-sftlf-EC-Earth3-T255.nc
  fx-sftlf-EC-Earth3-T511.nc
  nemo-vertices-ORCA1-t-grid.nc
  nemo-vertices-ORCA1-u-grid.nc
  nemo-vertices-ORCA1-v-grid.nc
  nemo-vertices-ORCA025-t-grid.nc
  nemo-vertices-ORCA025-u-grid.nc
  nemo-vertices-ORCA025-v-grid.nc
  omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-HR.nc
  omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR.nc
  omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR-pliocene.nc
  omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables.nc
 )

 # Test whether the directroy exists:
 if [ ! -d ${b2share_directroy} ]; then 
  echo; tput setaf 1;
  echo ' Error: The directroy' ${b2share_directroy} 'does not exist.'
  tput sgr0; echo
  exit
 fi

 echo
 # Check for each of the b2share ece2cmor dataset files whether they are available, if not the file
 # will be downloaded with wget:
 for b2share_file in "${b2share_files[@]}"; do
     if [ ! -f ${b2share_directroy}/${b2share_file} ]; then
      tput setaf 1;
      echo ' The file' ${b2share_file} 'will be downloaded.'
      tput sgr0
      
      wget --directory-prefix=${b2share_directroy}/ ${b2share_ece2cmor_dataset_address}/${b2share_file}
     else
      echo ' The file' ${b2share_file} 'is already available.'
     fi
 done
 echo

 # Checking whether all files are there:
 for b2share_file in "${b2share_files[@]}"; do
     if [ ! -f ${b2share_directroy}/${b2share_file} ]; then
      tput setaf 1;
      echo ' Warning: The file' ${b2share_directroy}/${b2share_file} 'it still does not exist after trying to download it.'
      tput sgr0
     fi
 done

 # Checking the md5 checksums:
 cd ${b2share_directroy}
 md5sum -c --quiet md5-checksum-b2share-data.md5
 cd -

else
 echo
 echo ' Illegal number of arguments: the script requires one argument: The path of the b2share-data directory:'
 echo ' ' $0 '${HOME}/cmorize/ece2cmor3-python-3/ece2cmor3/resources/b2share-data'
 echo ' ' $0 '${HOME}/cmorize/ece2cmor3-python-2/ece2cmor3/resources/b2share-data'
 echo ' ' $0 '${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/b2share-data'
 echo ' ' $0 '${PERM}/cmorize/ece2cmor3/ece2cmor3/resources/b2share-data'
 echo
fi


# https://b2share.eudat.eu/records/f7de9a85cbd443269958f0b80e7bc654  (Latest) Version - June 1, 2021
# fx-sftlf-EC-Earth3-T159.nc                                                             23.86 KB Checksum: md5:d6234951785381db616d5bd23e44bbf5 PID: 11304/8996528b-ce71-4dd9-9dcd-3d18b60d3ded
# fx-sftlf-EC-Earth3-T255.nc                                                             68.42 KB Checksum: md5:e9a03e54896ed4a8b571a63f51296565 PID: 11304/8c6dd0f7-77ef-4a6a-8628-b3f53c2ef3dc
# fx-sftlf-EC-Earth3-T511.nc                                                            104.35 KB Checksum: md5:67512db1813a44acd7cb7c1ad3e3609e PID: 11304/76160387-7ac2-4aae-8ce8-97961b9bc608
# nemo-vertices-ORCA025-t-grid.nc                                                        48.47 MB Checksum: md5:1cabb88e00a6ef9822e98c2feaa3bcd5 PID: 11304/2f00cedc-2bd6-469a-aabf-3b19d5195252
# nemo-vertices-ORCA025-u-grid.nc                                                        48.47 MB Checksum: md5:d89d30dba908802ae07d98a56334d136 PID: 11304/66462784-d8e2-42d5-8ff8-137957da9c97
# nemo-vertices-ORCA025-v-grid.nc                                                        48.47 MB Checksum: md5:d03b43abab29934eb63ab96b51847da4 PID: 11304/e88fa86d-4861-4bbc-943b-1ab95c55f6cb
# nemo-vertices-ORCA1-t-grid.nc                                                           3.40 MB Checksum: md5:d778dcd3936698fa87eca4fa06b367c0 PID: 11304/43ad2765-6f4d-4ec0-95dc-f12d43257e19
# nemo-vertices-ORCA1-u-grid.nc                                                           3.40 MB Checksum: md5:146d4dc73fcd637e41f2066e40db8c3d PID: 11304/e63de7f9-aba7-4b3f-9218-85f573bae644
# nemo-vertices-ORCA1-v-grid.nc                                                           3.40 MB Checksum: md5:33d04501d157c66e8e95be1e9638ebf7 PID: 11304/dd7022b1-8645-4447-87ef-2ca1cf5da9cf
# omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-HR.nc            2.17 MB Checksum: md5:c54131a0136c42ee6dd5dc24fe4f0ca8 PID: 11304/30c24e48-7c46-490a-917c-8db6387b817c
# omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR.nc          232.58 KB Checksum: md5:e54c25a3faf44486719848bfe3726055 PID: 11304/99fbb8ef-cd99-4e88-9075-505ce57be430
# omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR-pliocene.nc 232.60 KB Checksum: md5:138e5b01f4298dac3a29c387eda30069 PID: 11304/e2872b00-1fcd-470e-8b5b-b1cadf07cf8e
# omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables.nc             558.98 KB Checksum: md5:f6c975573143257c90b4ea4fe4333ab0 PID: 11304/7e3e4fd9-0b2d-443d-8fc4-3eac98b070ee
