#!/bin/bash

for MIP in {CMIP6,PRIMAVERA}; do
mkdir -p ${MIP}
    for f in ../cmip6-cmor-tables/Tables/${MIP}_*.json; do
        fname=$(basename $f)
        fname=${fname%.json}
        table=${fname#${MIP}_}
        ofile=${MIP}/${table}.csv
        echo "Converting data for ${table} to ${ofile}..."
        xlsx2csv -n ${table} -i PRIMAVERA_Data_Request.xlsx > ${ofile}
        if [ ! -s ${ofile} ]; then
            rm -f ${ofile}
        fi
    done
    ../../scripts/drq2json.py --drq ${MIP}/
    mv varlist.json ${MIP}/
done

