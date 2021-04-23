#!/usr/bin/env bash
# Thomas Reerink
#
# This script converts a component json file produced by genecec including the preferences
# into a flat json without the component structue (ifs, nemo, lpjg & tm5) such that it can be
# read with: checkvars --drq flat-json-file.json
#
# Note that when a flat json file is given (instead of a component json file) the produced json
# file will be just equal to the input flat json file.
#
# Run this script without arguments for examples how to call this script.
#

if [ "$#" -eq 1 ]; then

 input_json_file=$1
 output_json_file=${input_json_file##*/}
 output_json_file=${output_json_file/.json/-flat.json}

 # Convert vars json to drq json:
 sed -e '/"ifs":/d' -e '/"nemo":/d' -e '/"lpjg":/d' -e '/"tm5":/d' -e '/    },$/d' -e 's/        ]$/        ],/' ${input_json_file} | head --lines=-2 >  ${output_json_file}
 echo '        ]'                                                                                                                                     >> ${output_json_file}
 echo '}'                                                                                                                                             >> ${output_json_file}

 echo
 echo ' The script' $0 ' produced the file;'
 echo '  ' ${output_json_file}
 echo

else
 echo
 echo '  This scripts requires one argument, a json file, e.g.:'
 echo '  ' $0 knmi23-dutch-scenarios/historical-EC-EARTH-AOGCM-plev23r/cmip6-data-request-varlist-CMIP-historical-EC-EARTH-AOGCM.json
 echo
fi
