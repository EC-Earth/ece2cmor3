#!/usr/bin/sh
#
#SBATCH --account=...
#SBATCH --time=...
#SBATCH --nodes=1
#SBATCH --output=checksum.log
#SBATCH --exclusive

# Uses GNU parallel for parallesisation of checksum computation. Make sure it's
# available! (on NSC, load module parallel/...)

file_list="file.list"
checksum_file="sha256sums"

find CMIP6 -type f > $file_list

parallel -a $file_list sha256sum > $checksum_file
