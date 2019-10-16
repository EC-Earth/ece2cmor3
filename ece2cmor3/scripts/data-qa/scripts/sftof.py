#!/usr/bin/env python

import sys
import os
import shutil

from netCDF4 import Dataset    

if __name__=='__main__':

    variable_name = 'sftof'

    if len(sys.argv)!=2:
        raise RuntimeError('Need exactly one netcdf file as argument!')

    if not os.path.isfile(sys.argv[1]):
        raise RuntimeError('"{}" is not a file!'.format(sys.argv[1]))

    file_name = sys.argv[1]
    file_name_bak = '{}.bak'.format(file_name)

    if os.path.isfile(file_name_bak):
        raise RuntimeError('Backup file "{}" exists already!'.format(file_name_bak))

    shutil.copy2(src=file_name, dst=file_name_bak)

    dataset = Dataset(file_name, 'r+')
    try:
        data = 100 + 0*dataset.variables[variable_name][:]
    except KeyError:
        raise RuntimeError('Variable "{}" not found in "{}"!'.format(variable_name, file_name))

    dataset.variables[variable_name][:] = data
    dataset.close()
