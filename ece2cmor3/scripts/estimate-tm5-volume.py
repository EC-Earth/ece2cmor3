#!/usr/bin/env python

# Call this script e.g. by:
#  ./estimate-tm5-volume.py --vars cmip6-data-request/cmip6-data-request-m=CMIP-e=CMIP-t=1-p=1/cmvme_CMIP_piControl_1_1.xlsx
#  ./estimate-tm5-volume.py --vars cmip6-data-request/cmip6-data-request-m=AerChemMIP-e=CMIP-t=1-p=1/cmvme_AerChemMIP_amip_1_1.xlsx
#  ./estimate-tm5-volume.py --vars cmip6-data-request/cmip6-data-request-m=AerChemMIP-e=hist-1950HC-t=1-p=1/cmvme_AerChemMIP_hist-1950HC_1_1.xlsx
#
# This script estimates the volume of the output from TM5 for one MIP experiment.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script is called by the script:
#  generate-ec-earth-namelists.sh
#

import xml.etree.ElementTree as xmltree
import os.path                                                # for checking file or directory existence with: os.path.isfile or os.path.isdir
import sys                                                    # for aborting: sys.exit
from os.path import expanduser
import argparse
import logging

from ece2cmor3 import ece2cmorlib, taskloader, cmor_source, cmor_target, cmor_utils, components


# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Logger construction
log = logging.getLogger(__name__)


# Main program
def main():
    parser = argparse.ArgumentParser(description="Estimates the volume of the output from TM5 for a given CMIP6 data request for EC-Earth3")
    parser.add_argument("--vars", metavar="FILE", type=str, required=True,
                        help="File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")

    args = parser.parse_args()

    print ""
    print "Running estimate-tm5-volume.py with:"
    print "./estimate-tm5-volume.py --vars " + args.vars
    print ""

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default, mode=ece2cmorlib.PRESERVE, tabledir=args.tabdir,
                                        tableprefix=args.tabid)

    # Load only TM5 variables as task targets:
    active_components = {component: False for component in components.models}
    active_components["tm5"] = True
    taskloader.load_targets(args.vars, active_components=active_components)
    
    for task in ece2cmorlib.tasks:
    	 print ' {:15} {:8} {:15} {}'.format(task.target.variable, task.target.table, task.target.units, task.target.frequency)
        #print task.target.__dict__

    print ' Number of activated data request tasks is', len(ece2cmorlib.tasks)
        

    total_layer_equivalent= 0
    count = 0
    for task in ece2cmorlib.tasks:
      count = count + 1
      print ' {:15} {:8} {:15} {}'.format(task.target.variable, task.target.table, task.target.units, task.target.frequency)

      # TM5 Volume estimate: estimate the number of 2D layers per variable in output due to the number of time steps per year:
      if task.target.frequency == 'yr':
       layer_number_due_to_freq = 1
      elif task.target.frequency == 'mon':
       layer_number_due_to_freq = 12
      elif task.target.frequency == 'day':
       layer_number_due_to_freq = 365
      elif task.target.frequency == '3hrPt':
       layer_number_due_to_freq = 365.25 * 8.
      elif task.target.frequency == 'fx':
       layer_number_due_to_freq = 0
      elif task.target.frequency == 'monC':
       layer_number_due_to_freq = 1./30.        # Number of climate points: 1 per 30 year?
      elif task.target.frequency == 'subhrPt':
      #layer_number_due_to_freq = 365.25 * 12.  # At least hourly, thus sofar under limit (Actually there should't be (sub) houry variables available?).
       layer_number_due_to_freq = 0             # Because there won't be any subhourly output from TM5.
      else:
       print '\n Unknown frequency in TM5 Volume estimate for: ', task.target.variable, '\n'
       layer_number_due_to_freq = 0

      # TM5 Volume estimate: estimate the number vertical layers per variable:
      zdim=getattr(task.target, "z_dims", [])
      if len(zdim) == 0:
       vertical_dim = 1
      else:
       if zdim[0] == 'alevel':
        vertical_dim = 34
       elif zdim[0] == 'alevhalf':
        vertical_dim = 35
       elif zdim[0] == 'plev39':
        vertical_dim = 39
       elif zdim[0] == 'plev19':
        vertical_dim = 19
       else:
        vertical_dim = 1

      # TM5 Volume estimate: calculate the number of 2D layers in output due to the number of time steps & the number of vertical layers per year per variable:
      layers_per_var_per_yr = layer_number_due_to_freq * vertical_dim
      # TM5 Volume estimate: and for all variables together:
      total_layer_equivalent = total_layer_equivalent + layers_per_var_per_yr
     #print(' {:3} varname: {:15} freq: {:5} table: {:7} zdim: {:30} vertical dim: {:3} {:2} {:8} layers per var per yr: {:8}'.format(count, task.target.variable, task.target.frequency, task.target.table, getattr(task.target, "z_dims", []), vertical_dim, len(zdim), layer_number_due_to_freq, layers_per_var_per_yr ))

    print '\n With a 2D layer equivalent of ', total_layer_equivalent, ' the TM5 Volume estimate for this CMIP6 data request is ', total_layer_equivalent * 0.1 / 1000.0, ' GB per year\n'
    print ' The number of variables which is available from TM5 in EC-Erth3 for this experiment is', count

    volume_estimate = open('volume-estimate-tm5.txt','w')
    volume_estimate.write(' \nEC-Earth3 TM5 Volume estimates of generated output:{}'.format('\n'))
    volume_estimate.write('  Volume estimate for the TM5 3x2 degrees grid: {} GB/yr{}'.format(total_layer_equivalent * 0.1 / 1000.0, '\n'))
    volume_estimate.write('  With {:8} horizontal data slices per year across the vertical and time dimension.{}'.format(int(total_layer_equivalent), '\n\n'))
    volume_estimate.close()


    # Finishing up
    ece2cmorlib.finalize_without_cmor()



if __name__ == "__main__":
    main()
