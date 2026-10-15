#!/usr/bin/env python3
"""

 Creating the various file_def files for XIOS for ECE4 and the .ins file for LPJG in ECE4
 based on an XML CMIP7 data request file.

 For instance this CMIP7 XML data request file can be generated for the esm-hist experiment by:
  ./cmip7-request.py -a -e esm-hist -p high v1.2.2.5

 Call example:
  ./genecec-cmip7-file_def-files.py config-genecec-cmip7-file_def > genecec-cmip7-file_def-files.log

"""
import sys
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import expanduser

from list_dict_nemo import nemo_dict
from list_dict_oifs import oifs_dict
from list_dict_m7   import m7_dict

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message


def print_message_list(message_list):
    if len(message_list) > 0:
     for message in message_list:
      print(message)
     print()
    return

def root_of_xml_file(xml_file_name, file_description, verbose=False):
    if os.path.isfile(xml_file_name) == False:
     print(' The file {} does not exist.'.format(xml_file_name))
     sys.exit(' Stop in: {}'.format(sys.argv[0]))
    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(xml_file_name)
    if verbose: print(' Reading the {} file: {}'.format(file_description, pf[1]))
    # Load the xml file:
    tree_xml_file = ET.parse(xml_file_name)
    return tree_xml_file.getroot()

def write_xml_file_opening(xml_file_filename):
    Path(xml_file_filename).parent.mkdir(parents=True, exist_ok=True) # Ensure the dir and subdirs are created
    xml_file = open(xml_file_filename, 'w')
    xml_file.write('<?xml version="1.0"?>\n\n')
    xml_file.write('<file_definition min_digits="4" name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" type="one_file">\n')
    return xml_file

def write_xml_file_group_opening(xml_file, file_group_id):
    xml_file.write('  <file_group id="' + file_group_id + '" default_value="1e20" chunking_blocksize_target="3.0">\n')

def write_xml_file_group_closing(xml_file):
    xml_file.write('  </file_group>\n')
    return

def write_xml_file_closing(xml_file):
    xml_file.write('</file_definition>\n')
    xml_file.close()
    return

def write_xml_file_group(file_def_file, id_file_group, model_dict, verbose):
    write_xml_file_group_opening(file_def_file, id_file_group)
    for ii in model_dict:
     for jj in model_dict[ii]:
      for kk in model_dict[ii][jj]:
       if model_dict[ii][jj][kk] != []:
        # Write the non empty lists:
        if verbose: print(' {:12} {:8} {:8} {}'.format(ii, jj, kk, len(model_dict[ii][jj][kk])))
        write_file_group_body_to_xml_file(file_def_file, ii, jj, kk, model_dict[ii][jj][kk])
    write_xml_file_group_closing(file_def_file)
    return

def map_to_xios_freq(frequency):
    # Those frequency strings which differ in XIOS from CMIP7 are mapped:
    if   frequency == 'fx':
         frequency =  'once'
    elif frequency == 'day':
         frequency =  '1d'
    elif frequency == 'mon':
         frequency =  '1mo'
    elif frequency == 'yr':
         frequency =  '1yr'
    elif frequency == 'dec':
         frequency =  '10yr'
    return frequency

def write_file_group_body_to_xml_file(xml_file, grid, output_freq, region, list_with_xml_lines_of_group):
    # Add a group only if it has some content:
    if len(list_with_xml_lines_of_group) != 0:
    #if region == 's30': region = '30S-90S'
     if region == 's30': region = '30Sto90S'
     group_id  = grid.strip() + '_' + output_freq.strip() + '_' + region.strip()
     xios_freq = map_to_xios_freq(output_freq.strip())
    #xml_file.write('    <file id="group_{}" name_suffix="_{}" output_freq="{}">\n'.format(group_id, group_id, xios_freq))
     xml_file.write('    <file id="group_{}" name_suffix="_{}" output_freq="{}" grid_ref="grid_{}" region="{}">\n'.format(group_id, group_id, xios_freq, grid, region.replace('to', '-')))
     for xml_line in list_with_xml_lines_of_group:
      xml_file.write('{}\n'.format(xml_line))
     xml_file.write('    </file>\n')
    return

def determine_operation_value(element):
  if   element.get('branding_suffix')[:5] == 'tavg-':
   operation = 'average'
  elif element.get('branding_suffix')[:4] == 'tpt-':
   operation = 'instant'
  elif element.get('branding_suffix')[:5] == 'tmax-':
   operation = 'maximum'
  elif element.get('branding_suffix')[:5] == 'tmin-':
   operation = 'minimum'
  elif element.get('branding_suffix')[:3] == 'ti-':
   operation = 'once'
 #elif element.get('branding_suffix')[:3] == 'tmaxavg-':
 # operation = ''                                            # Achieve: Daily Maximum
 #elif element.get('branding_suffix')[:3] == 'tminavg-':
 # operation = ''                                            # Achieve: Daily Minimum
 #elif element.get('branding_suffix')[:3] == 'tclm-':
 # operation = ''                                            # Achieve: temporal_shape="climatology", i.e. a 30 year mean of monly means [Standard climatology (time2 dimensions)]
 #elif element.get('branding_suffix')[:3] == 'tclmdc-':
 # operation = ''                                            # Achieve: temporal_shape="diurnal-cycle", i.e. a 30 year mean of hourly means [diurnal mean climatology (a daily cycle pattern averaged over a reference climatological period), using the time3 dimension]
  else:
   operation = 'unknown'
  return operation

def generate_xml_line_for_variable(cmip7_element, field_id, verbosity):
    if cmip7_element.get('expression'):
     if cmip7_element.get('expression') != 'None':
      expression = cmip7_element.get('expression').replace('&','&amp;').replace('<','&lt;')
     else:
      expression = ''
    else:
     expression = ''

    # Taking the grid_ref, freq_op, freq_offset and operation from the ECE4 inherited field_def file if available:
    grid_ref    = ''
    operation   = ''
    freq_op     = ''
    freq_offset = ''
    # Set first the xpath search for iterating through the field_def file:
    xpath_expression_fd = './/field[@id="' + field_id + '"]'
    match_fd = 0
    for element_fd in root_ece_field_def.findall(xpath_expression_fd):
     if element_fd.get('grid_ref'   ): grid_ref    = element_fd.get('grid_ref')
     if element_fd.get('freq_op'    ): freq_op     = element_fd.get('freq_op')
     if element_fd.get('freq_offset'): freq_offset = element_fd.get('freq_offset')
     if element_fd.get('operation'  ): operation   = element_fd.get('operation')
     match_fd += 1
     if verbosity >= 2: print(' A  fd match for {:25} with i = {}'.format(field_id, match_fd))
    if match_fd == 0:
     if verbosity >= 1: print(' No fd match for {:25} with i = {}'.format(field_id, match_fd))
     # Initialisation required because this variable is an returned function argument.
     element_fd = None

    operation_based_on_branding = determine_operation_value(cmip7_element)
    if operation != operation_based_on_branding:
     # Filtering out those inherited which are an empty string:
     if operation != '':
      message = ' Warning: The inherited operation differs from the branding one: {:8} -vs- {:8} for {:23} for {}'.format( \
                   operation, \
                   operation_based_on_branding, \
                   field_id, \
                   cmip7_element.get('cmip7_compound_name'))
      message_list_of_operation_comparsion.append(message)
     # Give preference to the operation value from the CMIP7 branding:
     operation = operation_based_on_branding

    xml_line = ('      <field  enabled="True" '\
                             ' field_ref={:25}' \
                             ' priority={:10}' \
                             ' grid_ref={:20}' \
                             ' units={:20}' \
                             ' operation={:10}' \
                             ' freq_op={:20}' \
                             ' freq_offset={:20}' \
                             ' name={:55}' \
                             ' long_name={:132}' \
                             ' standard_name={:160}' \
                             ' modeling_realm={:33}' \
                             ' region={:12}' \
                             ' frequency={:12}' \
                             ' dimensions={:45}' \
                             ' branding_suffix={:25}' \
                             ' cmip6_table={:14}' \
                             ' physical_parameter_name={:28}' \
                             ' ifs_shortname={:13}' \
                             ' varname_code={:25}' \
                ' > {:81}</field>'.format( \
                '"' +                    field_id                  + '"', \
                '"' + cmip7_element.get('priority'               ) + '"', \
                '"' + grid_ref                                     + '"', \
                '"' + cmip7_element.get('units'                  ) + '"', \
                '"' + operation                                    + '"', \
                '"' + freq_op                                      + '"', \
                '"' + freq_offset                                  + '"', \
                '"' + cmip7_element.get('cmip7_compound_name'    ) + '"', \
                '"' + cmip7_element.get('long_name'              ) + '"', \
                '"' + cmip7_element.get('standard_name'          ) + '"', \
                '"' + cmip7_element.get('modeling_realm'         ) + '"', \
                '"' + cmip7_element.get('region'                 ) + '"', \
                '"' + cmip7_element.get('frequency'              ) + '"', \
                '"' + cmip7_element.get('dimensions'             ) + '"', \
                '"' + cmip7_element.get('branding_suffix'        ) + '"', \
                '"' + cmip7_element.get('cmip6_table'            ) + '"', \
                '"' + cmip7_element.get('physical_parameter_name') + '"', \
                '"' + cmip7_element.get('ifs_shortname'          ) + '"', \
                '"' + cmip7_element.get('varname_code'           ) + '"', \
                ' ' +                    expression                + ' ') \
               )
    return element_fd, xml_line

# Note: there are cases left which are not covered due to deviating dimensional shape and
# a lacking grid_ref definition (see the warning list). In case of a non earlier catched
# frequency or region, another warning will be given.
def add_xml_line_to_selected_group(cmip7_element, field_id, list_cluster, message_list):
    # Mapping of legacy basin diagnostics to NEMO 4.2, i.e. the XIOS field_ref and grid_ref:
    legacy_basin_diagnostics_map = {
      # 1. Total Transports (Note the structural name change to vtr)
      "sopht_vt_3bsn":  {"field_ref": "sophtvtr",  "grid_ref": "znl_T_2D"}, # Total Heat Transport
      "sopst_vs_3bsn":  {"field_ref": "sopstvtr",  "grid_ref": "znl_T_2D"}, # Alternative total salt transport name
      "sopst_vt_3bsn":  {"field_ref": "sopstvtr",  "grid_ref": "znl_T_2D"}, # Standard total Salt Transport
      # 2. Overturning Components (Stripped _3bsn)
      "sophtove_3bsn":  {"field_ref": "sophtove",  "grid_ref": "znl_T_2D"}, # Overturning Heat Transport
      "sopstove_3bsn":  {"field_ref": "sopstove",  "grid_ref": "znl_T_2D"}, # Overturning Salt Transport
      # 3. Gyre Components (Stripped _3bsn)
      "sophtgyre_3bsn": {"field_ref": "sophtgyre", "grid_ref": "znl_T_2D"}, # Gyre Heat Transport
      "sopstgyre_3bsn": {"field_ref": "sopstgyre", "grid_ref": "znl_T_2D"}, # Gyre Salt Transport
      # 4. Barotropic Components (Stripped _3bsn)
      "sophtbtr_3bsn":  {"field_ref": "sophtbtr",  "grid_ref": "znl_T_2D"}, # Barotropic Heat Transport
      "sopstbtr_3bsn":  {"field_ref": "sopstbtr",  "grid_ref": "znl_T_2D"}, # Barotropic Salt Transport
      # 5. Mesoscale Eddy Advection Fluxes (Stripped _3bsn)
      "sophteiv_3bsn":  {"field_ref": "sophteiv",  "grid_ref": "znl_T_2D"}, # Eddy Induced Heat Transport
      "sopsteiv_3bsn":  {"field_ref": "sopsteiv",  "grid_ref": "znl_T_2D"}, # Eddy Induced Salt Transport
      # 6. Lateral Diffusion / Mixing Components (Stripped _3bsn)
      "sophtldf_3bsn":  {"field_ref": "sophtldf",  "grid_ref": "znl_T_2D"}, # Lateral Diffusive Heat Transport
      "sopstldf_3bsn":  {"field_ref": "sopstldf",  "grid_ref": "znl_T_2D"}, # Lateral Diffusive Salt Transport
      # 7. Core Zonal Structural Variables (Note the W-staggering shift on overturning streamfunction)
      "zomsf_3bsn"   :  {"field_ref": "zomsf",     "grid_ref": "znl_W_3D"}, # Overturning Stream-Function
      "mld_3bsn"     :  {"field_ref": "zotem",     "grid_ref": "znl_T_3D"}, # Zonal Mean Temperature profile
    }
    if field_id in legacy_basin_diagnostics_map:
     print(' Legacy catch {:15}: New id: {:10} with grid_ref="{}"'.format(field_id, legacy_basin_diagnostics_map[field_id]['field_ref'], legacy_basin_diagnostics_map[field_id]['grid_ref']))

    zonal_reductions = {
        "stfhtn"  : "znl_T_3D",  # Ocean  Physics Diagnostics; znltem (nemo internal naming)
        "stfsan"  : "znl_T_3D",  # Ocean  Physics Diagnostics; znlsal (nemo internal naming)
        "bmgc_znl": "znl_T_2D",  # PISCES Zonal   Diagnostics (if compiled with BGC zonal averages)
    }

    model_component = cmip7_element.get('model_component')
    output_freq     = cmip7_element.get('frequency')
    region          = cmip7_element.get('region')
    if region == '30S-90S': region = 's30'
    # Generate the XML file line for one variable, also make the inherited field_def info of
    # this variable available at this level in this function:
    element_fd, xml_line = generate_xml_line_for_variable(cmip7_element, field_id, verbosity_level)
    # Note that this method does not create a new XML tree, but with the group knowledge the
    # XML file is directly written
    if   model_component == 'nemo':
     if element_fd == None:
          # The dimension deltasigt is a new scalar coordinate introduced in the CMIP7 Data Request. It stands for the density threshold criterion (Delta sigma_t) used to compute specific mixed layer properties\u2014most notably for variables like mlotstsq (Ocean Mixed Layer Thickness Square Defined by Delta Sigma-T of 0.03 kg m-3)
          # The dimension osurf (ocean surface) is a new coordinate introduced in the CMIP7 DR. It explicitly replaces legacy depth coordinate tags (like depth0m or d0m) for ocean variables sampled at the sea surface layer.
          # The iceband is related to the ncatice coordinate in NEMO.
          # The olayer coordinate (ocean layer) is another structural addition used in CMIP7 data requests. It tracks quantities that are integrated or evaluated over specific defined physical layers of the ocean column (such as the upper 100 m, the upper 200m, or mixed layer subsets) rather than continuous, full-depth 3D profiles.
          if   cmip7_element.get('dimensions') == 'longitude latitude time'           or \
               cmip7_element.get('dimensions') == 'longitude latitude time deltasigt' or \
               cmip7_element.get('dimensions') == 'longitude latitude time osurf'     or \
               cmip7_element.get('dimensions') == 'longitude latitude iceband time'   or \
               'longitude latitude time olayer' in cmip7_element.get('dimensions')       :
                 grid = 'T_2D'
          elif cmip7_element.get('dimensions') == 'longitude latitude olevel time':
                if   field_id[0] == 'u':
                      grid = 'U_3D'
                      print(' Inform: in olevel determination the grid_ref="U_3D" is set for {}'.format(field_id))
                elif field_id[0] == 'v':
                      grid = 'V_3D'
                      print(' Inform: in olevel determination the grid_ref="V_3D" is set for {}'.format(field_id))
                elif field_id[0] == 'w':
                      grid = 'W_3D'
                      print(' Inform: in olevel determination the grid_ref="W_3D" is set for {}'.format(field_id))
                else:
                      grid = 'T_3D'
                     #print(' Inform: in olevel determination the grid_ref="T_3D" is set for {}'.format(field_id))
          elif cmip7_element.get('dimensions') == 'time':
                 grid = 'time'
          elif field_id in legacy_basin_diagnostics_map:
                 # This needs a fix higher up, there where the ECE4 field_def file is created.
                 grid = legacy_basin_diagnostics_map[field_id]['grid_ref']
                 xml_line = xml_line.replace(field_id, legacy_basin_diagnostics_map[field_id]['field_ref'])
                 # Adhoc fix of alignment:
                 xml_line = xml_line.replace('priority="', '     priority="') # Fix alignment
                 xml_line = xml_line.replace(' > '       , '      > '       ) # Fix alignment
                 # Dirty fix for expressions:
                 xml_line = xml_line.replace('sopht_vt_3bsn', legacy_basin_diagnostics_map['sopht_vt_3bsn']['field_ref'])
                 xml_line = xml_line.replace('sopst_vs_3bsn', legacy_basin_diagnostics_map['sopst_vs_3bsn']['field_ref'])
         #elif field_id in zonal_reductions:
         #       grid = zonal_reductions[field_id]
         #elif "taum" in field_id or "tauo" in field_id:
         #       # 3. Ultimate structural default based on cell-type keywords in field names
         #       grid = 'T_2D'
          else:
                grid = 'other'
                message_list['grid'].append(' Warning: case {:3} not covered in {:4} part with element_fd = None with {:48} {:6} {:12} {}'.format( \
                         output_freq                                           , \
                         model_component.upper()                               , \
                         'dimensions="' + cmip7_element.get('dimensions') + '"', \
                         cmip7_element.get('priority')                         , \
                         cmip7_element.get('status')                           , \
                         cmip7_element.get('cmip7_compound_name')))
     else:
      if element_fd.get('grid_ref'):
       grid = element_fd.get('grid_ref').replace('grid_', '')
      else:
       grid = 'other'
    elif model_component == 'ifs' or \
         model_component == 'tm5'    :
    #if element_fd == None:
          if   cmip7_element.get('dimensions') == 'longitude latitude time'             or \
               cmip7_element.get('dimensions') == 'longitude latitude time1'               :
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude time height2m'    or \
               cmip7_element.get('dimensions') == 'longitude latitude time1 height2m'   or \
               cmip7_element.get('dimensions') == 'longitude latitude time4 height2m'      :
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude time height10m'   or \
               cmip7_element.get('dimensions') == 'longitude latitude time1 height10m'  or \
               cmip7_element.get('dimensions') == 'longitude latitude time4 height10m'     :
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude time height100m'  or \
               cmip7_element.get('dimensions') == 'longitude latitude time1 height100m'    :
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude time sdepth10cm'  or \
               cmip7_element.get('dimensions') == 'longitude latitude time1 sdepth10cm'    :
                grid = 'reduced_sfc'
          elif 'longitude latitude time p'  in cmip7_element.get('dimensions') or \
               'longitude latitude time1 p' in cmip7_element.get('dimensions')    :
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude':
                grid = 'reduced_sfc'
          elif cmip7_element.get('dimensions') == 'longitude latitude alevel time'      or \
               cmip7_element.get('dimensions') == 'longitude latitude alevel time1'     or \
               cmip7_element.get('dimensions') == 'longitude latitude alevel time2'        :
                grid = 'reduced_ml'
          elif cmip7_element.get('dimensions') == 'longitude latitude plev3 time1':
                grid = 'reduced_plev3'
          elif cmip7_element.get('dimensions') == 'longitude latitude plev7h time1':
                grid = 'reduced_plev7h'
          elif cmip7_element.get('dimensions') == 'longitude latitude plev19 time':
                grid = 'reduced_plev19'
          elif cmip7_element.get('dimensions') == 'latitude plev39 time':
                grid = 'lat_plev39'
          elif cmip7_element.get('dimensions') == 'time':
                grid = 'time'
          elif cmip7_element.get('dimensions') == 'longitude latitude sdepth time':
                grid = 'reduced_sfc_sdepth'
          elif cmip7_element.get('dimensions') == 'longitude latitude sdepth':
                grid = 'reduced_sfc_sdepth'
          else:
                grid = 'other'
                message_list['grid'].append(' Warning: case {:3} not covered in {:4} part with element_fd = None with {:48} {:6} {:12} {}'.format( \
                         output_freq                                           , \
                         model_component.upper()                               , \
                         'dimensions="' + cmip7_element.get('dimensions') + '"', \
                         cmip7_element.get('priority')                         , \
                         cmip7_element.get('status')                           , \
                         cmip7_element.get('cmip7_compound_name')))
    #else:
    # if element_fd.get('grid_ref'):
    #  grid = element_fd.get('grid_ref').replace('grid_', '')
    # else:
    #  grid = 'other'
    else:
     print(' Warning: Component {} not implemented yet here.'.format(model_component))

    if output_freq in ['fx', '1hr', '3hr', '6hr', 'day', 'mon', 'yr', 'dec']:
     if region in ['glb', 'nh', 'sh', 's30', 'grl']:
      list_cluster[grid][output_freq][region].append(xml_line)
     else:
      message_list['region'].append(' Warning: unknown region: {:20} {:7} {}'.format(grid, output_freq, region))
    else:
     message_list['freq'].append(' Warning: unknown output_freq: {:20} {:7} {}'.format(grid, output_freq, region))
    return

def map_to_lpjg_freq(frequency):
    # Determine the LPJG frequency naming in the .ins file
    if   frequency == 'day':
         lpjg_freq =  'daily'
    elif frequency == 'mon':
         lpjg_freq =  'monthly'
    elif frequency == 'yr':
         lpjg_freq =  'yearly'
    else:
         print(' Unknown LPJG frequency: {}'.format(element_dr.get('frequency')))
         sys.exit(' Stop in: {} due to unknown LPJG frequency'.format(sys.argv[0]))
    return lpjg_freq

def add_lpjg_ins_line(element_dr, list_of_lpjg_ins_lines, message_list_lpjg_ins_vars):
    # Determine the CMIP6 LPJG CMOR name for in the .ins file:
    lpjg_var  = element_dr.get('physical_parameter_name')
    lpjg_freq = map_to_lpjg_freq(element_dr.get('frequency'))
    # Compose the LPJG .ins line for the considered CMIP7 variable - frequency combination:
    lpjg_ins_file_line = 'file_{}_{} "{}_{}.out"'.format(lpjg_var, lpjg_freq, lpjg_var, lpjg_freq)
    # Append the .ins file line for this CMIP7 variable - frequency combination to the list of .ins lines:
    list_of_lpjg_ins_lines.append(lpjg_ins_file_line)
    # Besides, create a message list for this includive printing the cmip7_compound_name:
    message = ' {:66} {}'.format(lpjg_ins_file_line, element_dr.get('cmip7_compound_name'))
    message_list_lpjg_ins_vars.append(message)
    return

def write_lpjg_ins_file(lpjg_ins_file_filename, list_of_lpjg_ins_lines):
    Path(lpjg_ins_file_filename).parent.mkdir(parents=True, exist_ok=True) # Ensure the dir and subdirs are created
    lpjg_ins_file_file = open(lpjg_ins_file_filename, 'w')
    for lpjg_ins_line in list_of_lpjg_ins_lines:
     lpjg_ins_file_file.write('{}\n'.format(lpjg_ins_line))
    return


if len(sys.argv) == 2:

  if __name__ == "__main__": config = {}                       # python config syntax

  config_filename = sys.argv[1]                                # Reading the config file name from the argument line
  if os.path.isfile(config_filename) == False:                 # Checking if the config file exists
   print(error_message, ' The config file ', config_filename, '  does not exist.\n')
   sys.exit()
  exec(open(config_filename).read(), config)                   # Reading the config file

  # Echo the exact call of the script in the log messages:
  print(' Running:\n  {:} {:}\n'.format(sys.argv[0], sys.argv[1]))

  # The input files:
  dr_filename                 = os.path.expanduser(config['data_request_filename'      ]) # data_request_filename       = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-esm-hist-priority-ordered.xml'
  identified_filename         = os.path.expanduser(config['identified_filename'        ]) # identified_filename         = 'xml-files/genecec-cmip7/identify-ece4-cmip7/cmip7-request-v1.2.2.5-all-full-identified-freq-mc-prio.xml'
  ece_field_def_filename      = os.path.expanduser(config['ece_field_def_filename'     ]) # ece_field_def_filename      = 'xml-files/genecec-cmip7/ec-earth-definition/ec-earth-definition-inherited-neat-formatted.xml'

  # The outnput files:
  ece4_file_def_filename_nemo = os.path.expanduser(config['ece4_file_def_filename_nemo']) # ece4_file_def_filename_nemo = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ec-earth-4-file_def-nemo.xml'
  ece4_file_def_filename_oifs = os.path.expanduser(config['ece4_file_def_filename_oifs']) # ece4_file_def_filename_oifs = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ec-earth-4-file_def-oifs.xml'
  ece4_file_def_filename_m7   = os.path.expanduser(config['ece4_file_def_filename_m7'  ]) # ece4_file_def_filename_m7   = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ec-earth-4-file_def-m7.xml'
  ece4_file_def_filename_all  = os.path.expanduser(config['ece4_file_def_filename_all' ]) # ece4_file_def_filename_all  = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ec-earth-4-file_def.xml'
  ece4_lpjg_ins_filename      = os.path.expanduser(config['ece4_lpjg_ins_filename'     ]) # ece4_lpjg_ins_filename      = 'xml-files/genecec-cmip7/ec-earth-file_def-files/lpjg-cmip7-output.ins'

  # Options:
  verbosity_level             =                    config['verbosity_level'            ]  # verbosity_level             = 0          # Default 0     options: 0-3
  show_warnings               =                    config['show_warnings'              ]  # show_warnings               = True       # Default True  options: True, False


  # Loading the XML input files:
  root_dr            = root_of_xml_file(dr_filename           , 'data request'            , verbosity_level > 0)
  root_identified    = root_of_xml_file(identified_filename   , 'identified'              , verbosity_level > 0)
  root_ece_field_def = root_of_xml_file(ece_field_def_filename, 'ECE4 inherited field_def', verbosity_level > 0)

  list_of_lpjg_ins_lines               = []
  message_list_of_operation_comparsion = []
  message_list_lpjg_ins_vars           = []
  warnings_nemo = {'grid': [], 'freq': [], 'region' : []} # dict with three message lists
  warnings_oifs = {'grid': [], 'freq': [], 'region' : []} # dict with three message lists
  warnings_m7   = {'grid': [], 'freq': [], 'region' : []} # dict with three message lists

  i_dr = 0

  # Iterate over the variables in the (experiment) CMIP7 data request (including unidentified variables):
  for element_dr in root_dr.findall('.//variable'):
   i_dr += 1

   # Set the xpath search for iterating through the identified file:
   selected_attribute_dr       = 'cmip7_compound_name'
   selected_attribute_dr_value = element_dr.get(selected_attribute_dr)
   xpath_path_identified       = ".//variable"
   xpath_expression_identified = xpath_path_identified + '[@' + selected_attribute_dr + '="' + selected_attribute_dr_value + '"]'
   match_identified = 0
   for element_identified in root_identified.findall(xpath_expression_identified):
    match_identified += 1

    model_component = element_identified.get('model_component')
    if model_component == 'nemo':
     # The varname_code is based on the ECE ping file for NEMO via the request or identified files
     add_xml_line_to_selected_group(element_identified                     , \
                                    element_identified.get('varname_code') , \
                                    nemo_dict                              , \
                                    warnings_nemo                            \
                                   )
    elif model_component == 'ifs':
     # Handling the OIFS cases in order to create the OIFS file_def file
     add_xml_line_to_selected_group(element_identified                     , \
                                    element_identified.get('ifs_shortname'), \
                                    oifs_dict                              , \
                                    warnings_oifs                            \
                                   )
    elif model_component == 'tm5':
     # Handling the M7 cases in order to create the M7 file_def file
     add_xml_line_to_selected_group(element_identified                     , \
                                    element_identified.get('varname_code') , \
                                    m7_dict                                , \
                                    warnings_m7                              \
                                   )
    elif model_component == 'lpjg':
     # Handling the LPJG cases in order to create the LPJG configuration .ins file
     add_lpjg_ins_line(element_dr, list_of_lpjg_ins_lines, message_list_lpjg_ins_vars)
    else:
     print(' Warning: the component {} is not covered.'.format(model_component))


  print()
  # Write the NEMO file_def XML file with all the id's:
  ecearth_nemo_file_def_file = write_xml_file_opening(ece4_file_def_filename_nemo)
  write_xml_file_group(ecearth_nemo_file_def_file, 'id_file_group_ocean'     , nemo_dict, verbosity_level > 0)
  write_xml_file_closing(ecearth_nemo_file_def_file)

  print()
  # Write the OIFS file_def XML file with all the id's:
  ecearth_oifs_file_def_file = write_xml_file_opening(ece4_file_def_filename_oifs)
  write_xml_file_group(ecearth_oifs_file_def_file, 'id_file_group_atmosphere', oifs_dict, verbosity_level > 0)
  write_xml_file_closing(ecearth_oifs_file_def_file)

  print()
  # Write the M7 file_def XML file with all the id's:
  ecearth_m7_file_def_file = write_xml_file_opening(ece4_file_def_filename_m7)
  write_xml_file_group(ecearth_m7_file_def_file,   'id_file_group_atmosphere', m7_dict  , verbosity_level > 0)
  write_xml_file_closing(ecearth_m7_file_def_file)

  # In case we would prefer to have one XML file_def file for ECE4 (NEMO + OIFS + M7):
  ecearth_file_def_file = write_xml_file_opening(ece4_file_def_filename_all)
  write_xml_file_group(ecearth_file_def_file     , 'id_file_group_ocean'     , nemo_dict, False)
  write_xml_file_group(ecearth_file_def_file     , 'id_file_group_atmosphere', oifs_dict, False)
  write_xml_file_group(ecearth_file_def_file     , 'id_file_group_aerosol'   , m7_dict  , False)
  write_xml_file_closing(ecearth_file_def_file)

  # Writing the LPJG .ins congiguration file for the specified data request:
  write_lpjg_ins_file(ece4_lpjg_ins_filename, list_of_lpjg_ins_lines)

  # Test the XML syntax by loading these XML file_def files:
  root_ece_file_def_nemo = root_of_xml_file(ece4_file_def_filename_nemo, 'file_def')
  root_ece_file_def_oifs = root_of_xml_file(ece4_file_def_filename_oifs, 'file_def')
  root_ece_file_def_m7   = root_of_xml_file(ece4_file_def_filename_m7  , 'file_def')
  root_ece_file_def_all  = root_of_xml_file(ece4_file_def_filename_all , 'file_def')

  # Print the warning messages for fields which are not in the fd file:
  if show_warnings:
   # Print the message list for those variable-cases where the operation from inheriting differs
   # from the one deduced from the CMIP7 branding:
   print()
   print_message_list(message_list_of_operation_comparsion)

   print_message_list(warnings_nemo['grid'  ])
   print_message_list(warnings_oifs['grid'  ])
   print_message_list(warnings_m7  ['grid'  ])
   print_message_list(warnings_nemo['freq'  ])
   print_message_list(warnings_oifs['freq'  ])
   print_message_list(warnings_m7  ['freq'  ])
   print_message_list(warnings_nemo['region'])
   print_message_list(warnings_oifs['region'])
   print_message_list(warnings_m7  ['region'])

  # Print each .ins-file line with the CMIP7 compound name attached:
  if verbosity_level > 2:
   print_message_list(message_list_lpjg_ins_vars)

  print('\n The script {} has finished, the results can be found in the directory:\n  {}\n  {}\n  {}\n  {}\n  {}' \
        .format(sys.argv[0]                , \
                ece4_file_def_filename_nemo, \
                ece4_file_def_filename_oifs, \
                ece4_file_def_filename_m7  , \
                ece4_file_def_filename_all , \
                ece4_lpjg_ins_filename       \
               )
       )

else:
   print()
   print(' This script needs one argument: a config file name. E.g.:')
   print('  ', sys.argv[0], 'config-genecec-cmip7-file_def')
   print()
