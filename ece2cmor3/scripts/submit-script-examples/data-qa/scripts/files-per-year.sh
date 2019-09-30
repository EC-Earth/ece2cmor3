#!/usr/bin/env bash

set -eu

usage() {
    cat << EOT >&2
$(basename $0): Count the number of cmorised files per year.

Usage: $(basename $0) FIRST_YEAR LAST_YEAR DIR

EOT
}

error() {
    usage
    echo "ERROR: $1" >&2
    [ -z ${2+x} ] && exit 99
    exit $2
}

(( $# != 3 )) && error "$(basename $0) needs exactly 3 arguments"

first_year=$1
last_year=$2
directory=$3

set +u
(( "$first_year" < "$last_year" )) || \
    error "First two arguments do not specify a time range: \"$first_year\" \"$last_year\""
set -u
[ ! -d "$directory" ] && error "Third argument is not a directory: \"$directory\""

i=1
for y in $(seq $first_year $last_year)
do
    echo -n "$(printf '%03d' $i) $y: "
    find $directory -type f -name "*_$y*.nc" | wc -l
    i=$((i+1))
done

# Example file name patterns:
#
# > find  . -name '*_1850*.nc' | sed 's:.*\(_1850.*\.nc\):\1:' | sort -u
# _1850-1850.nc
# _185001-185012.nc
# _18500101-18501231.nc
# _185001010000-185012311800.nc
# _185001010000-185012312100.nc
# _185001010130-185012312230.nc
# _185001010430-185012312230.nc
# 
# > find  . -name '*_1857*.nc' | sed 's:.*\(_1857.*\.nc\):\1:' | sort -u
# _1857-1857.nc
# _185701-185712.nc
# _18570101-18571231.nc
# _185701010000-185712311800.nc
# _185701010000-185712312100.nc
# _185701010130-185712312230.nc
