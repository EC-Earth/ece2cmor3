#! /usr/bin/env python
""" Take a template file (sftlf_fx_EC-Earth3-Veg_TEMPLATE_r1i1p1f1_gr.nc),
    which has correct data values for fx/sftlf (land fraction) and create
    publishable files for all experiments given
"""

import os
import shutil
import uuid

from netCDF4 import Dataset

#        experiment_id   heap               activity_id    version      experiment                                            parent exp id       src type parent time units        br mthd      b_t_p  b_t_c
all = [ ('amip',         'heap-03-amip',    'CMIP',        'v20190711', 'AMIP',                                               'no parent',        'AGCM',  'no parent',             'no parent', 0.0, 0.0),
        ('historical',   'heap-02-hist',    'CMIP',        'v20190926', 'all-forcing simulation of the recent past',          'piControl',        'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
        ('piControl',    'heap-04-pict',    'CMIP',        'v20190712', 'pre-industrial control',                             'piControl-spinup', 'AOGCM', 'days since 1980-01-01', 'standard',  0.0, 0.0),
        ('ssp126',       'heap-05-ssp126',  'ScenarioMIP', 'v20190926', 'update of RCP2.6 based on SSP1',                     'historical',       'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
        ('ssp245',       'heap-06-ssp245',  'ScenarioMIP', 'v20190927', 'update of RCP4.5 based on SSP2',                     'historical',       'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
        ('ssp370',       'heap-07-ssp370',  'ScenarioMIP', 'v20190927', 'gap-filling scenario reaching 7.0 based on SSP3',    'historical',       'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
        ('ssp585',       'heap-08-ssp585',  'ScenarioMIP', 'v20190928', 'update of RCP8.5 based on SSP5',                     'historical',       'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
        ('ssp119',       'heap-12-ssp119',  'ScenarioMIP', 'v20190711', 'low-end scenario reaching 1.9 W m-2, based on SSP1', 'historical',       'AOGCM', 'days since 1850-01-01', 'standard',  0.0, 0.0),
       #('abrupt-4xCO2', 'heap-09-4xCO2',   'CMIP',        'v20190702', 'abrupt quadrupling of CO2',                          'piControl',        'AOGCM', 'days since 1850-01-01', 'standard',  0.0,     0.0),
       #('1pctCO2',      'heap-10-1pctCO2', 'CMIP',        'v20190702', '1 percent per year increase in CO2',                 'piControl',        'AOGCM', 'days since 1850-01-01', 'standard',  0.0,     0.0),
      ]

#ncdump -h /lustre3/projects/CMIP6/reerink/cmorised-results/cmor-cmip-historical/h003/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/historical/r1i1p1f1/part-2/Amon/hus/gr/v20190926/hus_Amon_EC-Earth3_historical_r1i1p1f1_gr_186101-186112.nc|grep branch_time_in_


template_file='sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc'

for experiment_id, \
        heap, \
        activity_id, \
        version, \
        experiment, \
        parent_experiment_id, \
        source_type, \
        parent_time_units, \
        branch_method, \
        branch_time_in_parent, \
        branch_time_in_child in all:

    dir_name = 'CMIP6/' + activity_id + '/EC-Earth-Consortium/EC-Earth3/' + experiment_id + '/r1i1p1f1/fx/sftlf/gr/' + version
    file_name = os.path.join(dir_name, 'sftlf_fx_EC-Earth3_' + experiment_id + '_r1i1p1f1_gr.nc')

    print(file_name)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    shutil.copy2(src=template_file, dst=file_name)

    ds = Dataset(file_name, 'r+')

    ds.experiment_id = experiment_id
    ds.activity_id = activity_id
    ds.experiment = experiment
    ds.parent_experiment_id = parent_experiment_id
    ds.source_type = source_type
    ds.parent_time_units = parent_time_units
    ds.branch_method = branch_method
    ds.branch_time_in_parent = branch_time_in_parent
    ds.branch_time_in_child = branch_time_in_child
    ds.tracking_id = 'hdl:21.14100/' + str(uuid.uuid4())
    ds.further_info_url = 'https://furtherinfo.es-doc.org/CMIP6.EC-Earth-Consortium.EC-Earth3.' + experiment_id + '.none.r1i1p1f1'

    ds.close()
