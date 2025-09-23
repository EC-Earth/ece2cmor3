#!/usr/bin/env python
# Thomas Reerink

# Run this script without arguments for examples how to call this script.

# 1. This script reads the Shaconemo xml ping files (the files which relate the NEMO code variable
# names with the CMOR names. Actually the current ping files are slightly modified by the EC-Earth
# community: some bug fixes and some added identification. NEMO code names which are labeled by
# 'dummy_' have not been identified by the Shaconemo and EC-Earth comunity and therefore can be
# deselected. The prefix 'CMIP6_' (and 'NEMO_') are omitted. If available and if not identical,
# preference can be given to the content of the expression attribute over the content of the text.
#
# 2. This script reads the four NEMO xml field_def files (the files which contain the basic info
# about the fields required by XIOS. These field_def files can either be taken from the EC-Earth4
# repository or from the Shaconemo repository. The four field_def files for ECE4 contain nearly
# 1369 variables with an id (9 id's occur twice) and 319 variables without an id but with a field_ref
# (Most variables with a field_ref have a name attribute, but 53 variables with a field_ref have no
# name attribute).

      # 3. The NEMO only excel xlsx CMIP6 data request file:
      #  create-nemo-only-list/nemo-only-list-cmip6-requested-variables.xlsx
      # is read, it has been created from the scripts directory by running:
      #  ./create-nemo-only-list/create-nemo-only-list.sh
      # by checking the non-dummy NEMO shaconemo ping file cmor variable list against the
      # full CMIP6 data request for all CMIP6 MIPs in which EC-Earth participates, i.e. for tier 3
      # and priority 3: about 320 unique cmor-table - cmor-variable-name combinations.
      #
   # 4. A few lists are created and/or modified, some renaming, and for instance selecting the
   # output frequency per field from the cmor table label.
   #
   # 5. The exentensive basic flat ec-earth cmip6 nemo XIOS input file template (the namelist or the
   # file_def file) is written by combining all the available data. In this file for each variable the
   # enable attribute is set to false, this allows another smaller program in ece2cmor3 to set those
   # variables on true which are asked for in the various data requests of each individual MIP
   # experiment.
   #
   # 6. A varlist.json can be generated which contains all nemo available variables, this file can be used
   # as data request to test the cmorization of all CMIP6 available nemo variables for all the MIP experiments.
   #
   # 7. The basic flat file_def file is read again, now all gathered info is part of this single xml
   # tree which allows a more convenient way of selecting.
   #
   # 8. A basic file_def is created by selecting on model component, output frequency and grid. For
   # each sub selection a file element is defined.
   #
   # 9. Produce a nemopar.json file with all the non-dummy ping file variables.
   #
   # 10. Just read the basic file_def in order to check in case of modifications to the script whether
   # the basic file_def file is still a valid xml file.


import xml.etree.ElementTree as ET
#from ece2cmor3 import cmor_target
import os                                                       # for checking file or directory existence with: os.path.isfile or os.path.isdir
import sys                                                      # for aborting: sys.exit
import numpy as np                                              # for the use of e.g. np.multiply
from os.path import expanduser
import logging

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message

# Logging configuration
#logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logformat  =             "%(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)

# Logger construction
log = logging.getLogger(__name__)

def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Part {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')

if len(sys.argv) == 2:

   if __name__ == "__main__": config = {}                       # python config syntax

   config_filename = sys.argv[1]                                # Reading the config file name from the argument line
   if os.path.isfile(config_filename) == False:                 # Checking if the config file exists
    print(error_message, ' The config file ', config_filename, '  does not exist.\n')
    sys.exit()
   exec(open(config_filename).read(), config)                   # Reading the config file

   # Echo the exact call of the script in the log messages:
   logging.info('Running:\n\n {:} {:}\n'.format(sys.argv[0], sys.argv[1]))

   # Take the config variables:
   ece2cmor_root_directory                          = os.path.expanduser(config['ece2cmor_root_directory'                         ]) # ece2cmor_root_directory                          = '~/cmorize/ece2cmor3/'

   ping_file_name_ocean                             = os.path.expanduser(config['ping_file_name_ocean'                            ]) # ping_file_name_ocean                             = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/ping_ocean_DR1.00.27.xml'
   ping_file_name_seaIce                            = os.path.expanduser(config['ping_file_name_seaIce'                           ]) # ping_file_name_seaIce                            = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/ping_seaIce_DR1.00.27.xml'
   ping_file_name_ocnBgchem                         = os.path.expanduser(config['ping_file_name_ocnBgchem'                        ]) # ping_file_name_ocnBgchem                         = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/ping_ocnBgChem_DR1.00.27.xml'

   ecearth_ping_file                                = os.path.expanduser(config['ecearth_ping_file'                               ]) # ecearth_ping_file                                = 'ec-earth-ping.xml'            # The one which is not canonicalized
   ecearth_ping_file_canonic                        = os.path.expanduser(config['ecearth_ping_file_canonic'                       ]) # ecearth_ping_file_canonic                        = 'ec-earth-ping-canonic.xml'    # The one which is     canonicalized

   field_def_file_ocean                             = os.path.expanduser(config['field_def_file_ocean'                            ]) # field_def_file_ocean                             = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/field_def_nemo-opa.xml'
   field_def_file_seaice                            = os.path.expanduser(config['field_def_file_seaice'                           ]) # field_def_file_seaice                            = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/field_def_nemo-lim.xml'
   field_def_file_ocnchem                           = os.path.expanduser(config['field_def_file_ocnchem'                          ]) # field_def_file_ocnchem                           = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/field_def_nemo-pisces.xml'
   field_def_file_innerttrc                         = os.path.expanduser(config['field_def_file_innerttrc'                        ]) # field_def_file_innerttrc                         = '~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/field_def_nemo-inerttrc.xml'

   basic_flat_file_def_file_name                    = os.path.expanduser(config['basic_flat_file_def_file_name'                   ]) # basic_flat_file_def_file_name                    =  ece2cmor_root_directory + "ece2cmor3/resources/xios-nemo-file_def-files/basic-flat-cmip6-file_def_nemo.xml"
   basic_file_def_file_name                         = os.path.expanduser(config['basic_file_def_file_name'                        ]) # basic_file_def_file_name                         =  ece2cmor_root_directory + "ece2cmor3/resources/xios-nemo-file_def-files/basic-cmip6-file_def_nemo.xml"

   message_ping_expression_selection                =                    config['message_ping_expression_selection'               ]  # message_ping_expression_selection                = False
  #message_occurence_identical_id                   =                    config['message_occurence_identical_id'                  ]  # message_occurence_identical_id                   = False
   include_root_field_group_attributes              =                    config['include_root_field_group_attributes'             ]  # include_root_field_group_attributes              = False
   exclude_dummy_fields                             =                    config['exclude_dummy_fields'                            ]  # exclude_dummy_fields                             = True   # Keep this on True
   give_preference_to_pingfile_expression_attribute =                    config['give_preference_to_pingfile_expression_attribute']  # give_preference_to_pingfile_expression_attribute = True
  #include_grid_ref_from_field_def_files            =                    config['include_grid_ref_from_field_def_files'           ]  # include_grid_ref_from_field_def_files            = True
   produce_varlistjson_file                         =                    config['produce_varlistjson_file'                        ]  # produce_varlistjson_file                         = True


   # Run ece2cmor's install & check whether an existing ece2cmor root directory is specified in the config file:
   previous_working_dir = os.getcwd()
   if os.path.isdir(ece2cmor_root_directory) == False:
    print(error_message, ' The ece2cmor root directory ', ece2cmor_root_directory, ' does not exist.\n')
    sys.exit()
   if os.path.isfile(ece2cmor_root_directory + '/environment.yml') == False:
    print(error_message, ' The ece2cmor root directory ', ece2cmor_root_directory, ' is not an ece2cmor root directory.\n')
    sys.exit()
   os.chdir(ece2cmor_root_directory)
   os.system('pip install -e .')
   os.chdir(previous_working_dir)


   ################################################################################
   ###                                    1                                     ###
   ################################################################################
   print_next_step_message(1, 'READING THE PING FILES')

   ping_file_collection = [ping_file_name_ocean    , \
                           ping_file_name_seaIce   , \
                           ping_file_name_ocnBgchem  \
                          ]

   # Create the basic main structure which will be populated with the elements of the various ping files later on:
   root_main_ping = ET.Element('ecearth_ping')
   ET.SubElement(root_main_ping, 'ecearth_nemo_ping')
   ET.SubElement(root_main_ping, 'ecearth_oifs_ping')
   ET.SubElement(root_main_ping, 'ecearth_lpjg_ping')
   ET.indent(root_main_ping, space='  ')
  #ET.dump(root_main_ping)
  #print()

   # Create the tree object for the fresh created root for our main structure:
   tree_main_ping = ET.ElementTree(root_main_ping)

   total_pinglist_id        = []
   total_pinglist_field_ref = []
   total_pinglist_text      = []
   total_pinglist_expr      = []

   # Loop over the various ping files:
   for ping_file in ping_file_collection:
    if os.path.isfile(ping_file) == False: print(' The ping file {} does not exist.'.format(ping_file)); sys.exit(' stop')

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(ping_file)
    print(' Reading the file: {}'.format(pf[1]))

    # Load the xml file:
    tree_ping = ET.parse(ping_file)
    root_ping = tree_ping.getroot()

    # Add a new attribute original_file to each field_definition tag of the ping file:
    for element in root_ping.findall(".//field_definition"):
     element.set("original_file", pf[1])

   #ET.dump(root_ping) # Test

    # Append the root element of each field_def file to the level of ecearth_nemo_ping in the new ping file:
    for element in root_main_ping.findall(".//ecearth_nemo_ping"):
     element.append(root_ping)

    # For neat indentation, but also for circumventing the newline trouble:
    ET.indent(tree_main_ping, space='  ')

    # Only subelements can be removed, therefore select the parent level and apply the deselection from that level:
    count = 0
    for element in root_main_ping.findall('.//field_definition'):
     for elem in element.findall('./field'):
      if elem.attrib['field_ref'] == "dummy_XY" or elem.attrib['field_ref'] == "dummy_XYO":
       element.remove(elem)
      else:
       count+=1
       # Remove the CMIP6_ prefix from the ids:
       if elem.attrib['id'][0:6] == "CMIP6_":
        elem.set('id',elem.get('id')[6:])
       # Remove the NEMO_ prefix from the ids:
       if elem.attrib['id'][0:5] == "NEMO_":
        elem.set('id',elem.get('id')[5:])

       # Consistency check between the NEMO ping file xml content field and the ping file "expr"-attribute. They are not the same,
       # in the "expr"-attribute the time average operator @ is applied on each variable. So here spaces and the @ operator are
       # removed (at both sides) and only thereafter both are compared:
       if "expr" in elem.attrib:
        # Check on consistency between the expression and text in the NEMO ping fields:
        if elem.get('expr').replace(" ", "").replace("@", "")  != elem.text.replace(" ", "").replace("@", ""):
         print(' Mismatch between ping content and ping expr for variable {:12}: {:60} and {}'.format(elem.get('id'), elem.get('expr').replace(" ", "").replace("@", ""), elem.text.replace(" ", "").replace("@", "")))
        if give_preference_to_pingfile_expression_attribute:
         # Give preference to the content in expression attribute: Overwrite the text content with this expression content:
         elem.text = elem.get('expr')
         if message_ping_expression_selection:
          print(' For {:12} overwrite the expression in the ping file by the "expr"-attribute: {:60} -> {}'.format(elem.get('id'), elem.text, elem.get('expr')))
      #else:
      # print('No expression for: {}'.format(elem.get('id')))

   print('\n Number of ping fields: {}\n'.format(count))

   # Writing the combined result to a new xml file:
   tree_main_ping.write(ecearth_ping_file)


   # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
   with open(ecearth_ping_file_canonic, mode='w', encoding='utf-8') as out_file:
    ET.canonicalize(from_file=ecearth_ping_file, with_comments=True, out=out_file)

else:
   print()
   print(' This script needs one argument: a config file name. E.g.:')
   print('  ', sys.argv[0], 'config-create-basic-ecearth4-cmip7-xios-configuration-file')
   print()



#   # Unfortunately a more versatile solution like below does not work:
#   for element in root_main_ping.findall('.//field'):
#    if element.attrib['field_ref'] == "dummy_XY" or element.attrib['field_ref'] == "dummy_XYO":
#     root_main_ping.remove(element)

#   for element in root_main_ping.findall('.//field[@field_ref="dummy_XY"]'):
#    print('test: {}'.format(element.attrib['field_ref']))
#    root_main_ping.remove(element)
