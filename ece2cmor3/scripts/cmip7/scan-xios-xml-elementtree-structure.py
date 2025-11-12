#!/usr/bin/env python3
"""

 Scanning the XML structure of a set of XIOS field_def files:

 Call example:
  ./scan-xios-xml-elementtree-structure.py > scan.log

"""
import sys
import os
import subprocess
import argparse
import xml.etree.ElementTree as ET
import json
from collections import OrderedDict

def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Test {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')


def main():

 field_def_file_inn = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_nemo-innerttrc.xml.j2'
 field_def_file_pis = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_nemo-pisces.xml.j2'
 field_def_file_ice = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_nemo-ice.xml.j2'
 field_def_file_oce = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_nemo-oce.xml.j2'
 field_def_file_ifs = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_oifs_raw.xml.j2'
 field_def_file_lpj = '/home/reerink/ec-earth/ecearth4/scripts/runtime/templates/xios/field_def_lpjg.xml.j2'               # Not existing yet

 field_def_file_collection = [field_def_file_inn, \
                              field_def_file_pis, \
                              field_def_file_ice, \
                              field_def_file_oce, \
                             #field_def_file_lpj, \
                              field_def_file_ifs  \
                             ]

 if True:
  # Scan the field_def file stucture, how many layers (child, grandchild and so on). Discover whether a field_group and field
  # element are defined at the same level. Or whether within a field_group another field_group is defined. Check for other tags
  # than "field" and field_group (this is currently not the case).
  print_next_step_message(1, 'Scan the field_def file stucture')

  # Loop over the various field_def files:
  for field_def_file in field_def_file_collection:
   if os.path.isfile(field_def_file) == False: print(' The field_def file {} does not exist.'.format(field_def_file)); sys.exit(' stop')

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(field_def_file)
   print('\n\n {}\n'.format(pf[1]))

   # Load the xml file:
   tree = ET.parse(field_def_file)
   root = tree.getroot()

   i = 0
   j = 0
   detected_elements = []
   for child in root:
    if child.tag == 'field':
     i += 1
    if child.tag == 'field_group':
     j += 1
    if child.tag not in detected_elements:
     detected_elements.append(child.tag)
     print(' Detected another element at level 1: {}'.format(child.tag))
   print('                        Number of field is {:3} & number of field_group is {:3} for level 1'.format(i, j))

   i = 0
   j = 0
   detected_elements = []
   for child in root:
    for grandchild in child:
     if grandchild.tag == 'field':
      i += 1
     if grandchild.tag == 'field_group':
      j += 1
     if grandchild.tag not in detected_elements:
      detected_elements.append(grandchild.tag)
      print(' Detected another element at level 2: {}'.format(grandchild.tag))
   print('                        Number of field is {:3} & number of field_group is {:3} for level 2'.format(i, j))

   i = 0
   j = 0
   detected_elements = []
   for child in root:
    for grandchild in child:
     for ggrandchild in grandchild:
      if ggrandchild.tag == 'field':
       i += 1
      if ggrandchild.tag == 'field_group':
       j += 1
      if ggrandchild.tag not in detected_elements:
       detected_elements.append(ggrandchild.tag)
       print(' Detected another element at level 3: {}'.format(ggrandchild.tag))
   print('                        Number of field is {:3} & number of field_group is {:3} for level 3'.format(i, j))

   i = 0
   j = 0
   detected_elements = []
   for child in root:
    for grandchild in child:
     for ggrandchild in grandchild:
      for gggrandchild in ggrandchild:
       if gggrandchild.tag == 'field':
        i += 1
       if gggrandchild.tag == 'field_group':
        j += 1
       if gggrandchild.tag not in detected_elements:
        detected_elements.append(gggrandchild.tag)
        print(' Detected another element at level 4: {}'.format(gggrandchild.tag))
   print('                        Number of field is {:3} & number of field_group is {:3} for level 4'.format(i, j))



 if True:
  # Show for a certain xpath expression for a certain selected attribute for a certain xpath path which elements are selected:
  print_next_step_message(2, 'Show the selected elements for a certain xpath expression')

  selected_attribute = 'field_ref'
  selected_attribute = 'id'
 #xpath_path         = "./field_group/field_group/"            # Looping over only the field_group elements in the field_group/field_group/       layer
  xpath_path         = "./field_group/"                        # Looping over only the field_group elements in the field_group/                   layer
 #xpath_path         = ".//field_group"                        # Looping over all      field_group elements in any                                layer
 #xpath_path         = "./field_group/field_group/field/"      # Looping over only the field       elements in the field_group/field_group/field/ layer
 #xpath_path         = "./field_group/field/"                  # Looping over only the field       elements in the field_group/                   layer
 #xpath_path         = "./field/"                              # Looping over only the field       elements in the field                          layer  id: agrif_spf, ahmf_2d, ahmf_3d
 #xpath_path         = ".//field"                              # Looping over all      field       elements in any                                layer
  xpath_expression   = xpath_path + "[@" + selected_attribute + "]"

  print(' The used xpath expression is: {}'.format(xpath_expression))


  # Loop again over the various field_def files:
  for field_def_file in field_def_file_collection:
   if os.path.isfile(field_def_file) == False: print(' The field_def file {} does not exist.'.format(field_def_file)); sys.exit(' stop')

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(field_def_file)
   print('\n\n {}\n'.format(pf[1]))

   # Load the xml file:
   tree = ET.parse(field_def_file)
   root = tree.getroot()

   i = 0
   for element in root.findall(xpath_expression):
    i += 1
    print('{:4} {} {:25} {}'.format(i, element.tag, element.get(selected_attribute), element.attrib))



 if True:
  # Loop over all field & field_group elements at all levels and check whether they have at least a field_ref or an id. And count the number of field elements.
  print_next_step_message(3, 'Check if at least a field_ref or an id attribute is present')

  tags = ['field', 'field_group']
  for tag in tags:
   xpath_expression = ".//" + tag
   i_total = 0

   # Loop again over the various field_def files:
   for field_def_file in field_def_file_collection:
    if os.path.isfile(field_def_file) == False: print(' The field_def file {} does not exist.'.format(field_def_file)); sys.exit(' stop')

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(field_def_file)

    # Load the xml file:
    tree = ET.parse(field_def_file)
    root = tree.getroot()

    # Conclusion after running this: For every field element either an id or a field_ref attribute is present in all field elements in all field_def files.
    # In a few cases when a field_ref attribute is present an id attribute is specified as well in the field_def files for a field element.
    i_f           = 0  # The number of field elements
    i_id_or_fr    = 0  # The number of field elements with    a field_ref attribute or an id attribute
    i_no_id_or_fr = 0  # The number of field elements without a field_ref attribute and without an id attribute. This should not occur and thus be zero
    for element in root.findall(xpath_expression):
     i_f += 1
     if element.get('id') or element.get('field_ref'):
      i_id_or_fr += 1
     else:
      i_no_id_or_fr += 1
      print(' ERROR: A {} element without an id attribute and without a field_ref attribute has been detecetd. This should never occur!'.format(element.tag))
    print(' {:4} {:12} elements in the field_def file {}'.format(i_f, element.tag, field_def_file))
    i_total = i_total + i_f

   print('\n {:4} {:12} elements in all the field_def files.\n'.format(i_total, element.tag))



 if True:
  # Loop over all field & field_group elements at all levels and check more about the explicit field_ref and grid_ref attribute
  # inclusion for the elements (leaving out inheritage here)
  print_next_step_message(4, 'Loop over all tags with a field_ref attribute, check if id is present')

  verbose_level = 0

  tags = ['field', 'field_group']
  for tag in tags:
   xpath_expression = ".//" + tag
   i_total_fr           = 0
   i_total_no_fr        = 0
   i_total_fr_and_id    = 0
   i_total_fr_and_gr    = 0
   i_total_no_fr_and_gr = 0

   # Loop again over the various field_def files:
   for field_def_file in field_def_file_collection:
    if os.path.isfile(field_def_file) == False: print(' The field_def file {} does not exist.'.format(field_def_file)); sys.exit(' stop')

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(field_def_file)

    # Load the xml file:
    tree = ET.parse(field_def_file)
    root = tree.getroot()

    # For every field element either an id or a field_ref attribute is present in all field elements in all field_def files.
    # In a few caseses when a field_ref attribute is present an id attribute is specified as well in the field_def files for a field element.
    i_f            = 0  # The number of field elements
    i_fr           = 0  # The number of field elements with    a field_ref attribute
    i_no_fr        = 0  # The number of field elements without a field_ref attribute
    i_fr_and_id    = 0  # The number of field elements with    a field_ref attribute and with an id attribute
    i_fr_and_gr    = 0  # The number of field elements with    a field_ref attribute and with a  grid_ref attribute
    i_no_fr_and_gr = 0  # The number of field elements without a field_ref attribute and with a  grid_ref attribute
    for element in root.findall(xpath_expression):
     i_f += 1
     if element.get('field_ref'):
      # The field elements with a field_ref attribute (some have an id attribute as well)
      i_fr += 1
      field_ref_info = 'has a  field_ref {:27}'.format(element.get('field_ref'))
      if element.get('id'):
       i_fr_and_id += 1
       id_info = 'has    id {:27}'.format(element.get('id'))
      else:
       id_info = 'has no id {:27}'.format('')

      # Check for grid_ref attribute in case a field_ref attribute is available:
      if element.get('grid_ref'):
       i_fr_and_gr += 1
       grid_ref_info = 'has    grid_ref {}'.format(element.get('grid_ref'))
      else:
       grid_ref_info = 'has no grid_ref {}'.format(element.get('grid_ref'))

     else:
      # The field elements without a field_ref attribute, they all have an id attribute:
      i_no_fr += 1
      field_ref_info = 'has no field_ref {:27}'.format('')
      if element.get('id'):
       id_info = 'has    id {:27}'.format(element.get('id'))
      else:
       id_info = 'has no id {:27}'.format('')
       if verbose_level == 1: print(' ERROR: A {} element has no id attribute and no field_ref attribute. This should not occur!'.format(element.tag))

      # Check for grid_ref attribute in case no field_ref attribute is available:
      if element.get('grid_ref'):
       i_no_fr_and_gr += 1
       grid_ref_info = 'has    grid_ref {}'.format(element.get('grid_ref'))
      else:
       grid_ref_info = 'has no grid_ref {}'.format(element.get('grid_ref'))

     if verbose_level > 0: print(' A {} element {} and {} and {}'   .format(element.tag, field_ref_info, id_info, grid_ref_info))


    print(' {:4} {:12} elements with a field_ref attribute, {:3} with field_ref & grid_ref attribute, {:3} without field_ref & with grid_ref attribute in the field_def file {}'.format(i_fr, element.tag, i_fr_and_gr, i_no_fr_and_gr, pf[1]))
    i_total_fr           = i_total_fr           + i_fr
    i_total_no_fr        = i_total_no_fr        + i_no_fr
    i_total_fr_and_id    = i_total_fr_and_id    + i_fr_and_id
    i_total_fr_and_gr    = i_total_fr_and_gr    + i_fr_and_gr
    i_total_no_fr_and_gr = i_total_no_fr_and_gr + i_no_fr_and_gr

   print('\n {:4} {:12} elements with a  field_ref attribute in all the field_def files and {:3} of them have an id       attribute.'  .format(i_total_fr   , element.tag, i_total_fr_and_id))
   print(  ' {:4} {:12} elements with a  field_ref attribute in all the field_def files and {:3} of them have a  grid_ref attribute.'  .format(i_total_fr   , element.tag, i_total_fr_and_gr))
   print(  ' {:4} {:12} elements with no field_ref attribute in all the field_def files and {:3} of them have a  grid_ref attribute.\n'.format(i_total_no_fr, element.tag, i_total_no_fr_and_gr))



 if True:
  print_next_step_message(5, 'Combine the field_def files')

  ecearth_field_def_filename         = 'ec-earth-definition.xml'                # The one which is not canonicalized
  ecearth_field_def_filename_canonic = 'ec-earth-definition-canonic.xml'        # The one which is     canonicalized
  ecearth_field_def_nf_filename      = 'ec-earth-definition-neat-formatted.xml' # The one with the neat formatted (nf) format with a controlled order of the attributes


  # Create the basic main structure which will be populated with the elements of the various field_def files later on:
  root_main = ET.Element('ecearth_field_definition')
  ET.SubElement(root_main, 'ecearth4_nemo_field_definition')
  ET.SubElement(root_main, 'ecearth4_oifs_field_definition')
  ET.SubElement(root_main, 'ecearth4_lpjg_field_definition')
  ET.indent(root_main, space='  ')
 #ET.dump(root_main)

  # Create the tree object for the fresh created root for our main structure:
  tree_main = ET.ElementTree(root_main)

  if False:
   # The xml file with the basic structure can be optionally written to a file now:
   ecearth_field_def_filename_tmp = 'ec-earth-main-structure-tmp.xml'  # The one which is not canonicalized
   ecearth_field_def_filename     = 'ec-earth-main-structure.xml'      # The one which is     canonicalized

   # Write the basic xml structure to a file:
   tree_main.write(ecearth_field_def_filename_tmp)
   # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
   with open(ecearth_field_def_filename, mode='w', encoding='utf-8') as out_file:
    ET.canonicalize(from_file=ecearth_field_def_filename_tmp, with_comments=True, out=out_file)

   if False:
    # And optionally read the basic main structure from this file:
    pf = os.path.split(ecearth_field_def_filename)
    print('\n\n {}\n'.format(pf[1]))

    # Load the xml file:
    tree_main = ET.parse(ecearth_field_def_filename)
    root_main = tree_main.getroot()


  # Loop again over the various field_def files:
  for field_def_file in field_def_file_collection:
   if os.path.isfile(field_def_file) == False: print(' The field_def file {} does not exist.'.format(field_def_file)); sys.exit(' stop')

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(field_def_file)
   print('\n\n {}\n'.format(pf[1]))

   # Load the xml file:
   tree = ET.parse(field_def_file)
   root = tree.getroot()
  #print(' {} {}'.format(root.tag, root.attrib))

   # Add a new attribute original_file to each field_definition tag:
   root.set("original_file", pf[1])

   # Append the root element of each field_def file to the level of the ecearth4_*_field_definition in the new field_def file:
   if field_def_file == field_def_file_ifs:
    xpath_for_merge = ".//ecearth4_oifs_field_definition"
   elif field_def_file == field_def_file_lpj:
    xpath_for_merge = ".//ecearth4_lpjg_field_definition"
   else:
    xpath_for_merge = ".//ecearth4_nemo_field_definition"
   for element in root_main.findall(xpath_for_merge):
    element.append(root)

  # For neat indentation, but also for circumventing the newline trouble:
  ET.indent(tree_main, space='  ')

  # Writing the combined result to a new xml file:
  tree_main.write(ecearth_field_def_filename)

  # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
  with open(ecearth_field_def_filename_canonic, mode='w', encoding='utf-8') as out_file:
   ET.canonicalize(from_file=ecearth_field_def_filename, with_comments=True, out=out_file)

  # Read the just created ecearth_field_def_filename:
  tree_ecearth_field_def = ET.parse(ecearth_field_def_filename)
  root_ecearth_field_def = tree_ecearth_field_def.getroot()

  # One neat formatted field_def file including all compnent field_def files is created with a controlled order of the attributes:
  with open(ecearth_field_def_nf_filename, 'w') as ecearth_field_def_nf:
   tag_path = []
   for event, elem_nf in ET.iterparse(ecearth_field_def_filename, events=("start", "end")):

       if event == 'start':
        tag_path.append(elem_nf.tag)
        indentation = ' ' * 2 * (len(tag_path) - 1)
       #print(' start: event = {:7} element = {}'.format(event, elem_nf.tag))
        if elem_nf.tag == 'field':
        #ecearth_field_def_nf.write('{}<{}  '.format(indentation, elem_nf.tag))
         ecearth_field_def_nf.write('          <{}'.format(elem_nf.tag))

         attribute_id                   = 'id="'                   + str(elem_nf.get('id'))                   + '"'
         attribute_field_ref            = 'field_ref="'            + str(elem_nf.get('field_ref'))            + '"'
         attribute_enabled              = 'enabled="'              + str(elem_nf.get('enabled'))              + '"'
         attribute_unit                 = 'unit="'                 + str(elem_nf.get('unit'))                 + '"'
         attribute_grid_ref             = 'grid_ref="'             + str(elem_nf.get('grid_ref'))             + '"'
         attribute_axis_ref             = 'axis_ref="'             + str(elem_nf.get('axis_ref'))             + '"'
         attribute_name                 = 'name="'                 + str(elem_nf.get('name'))                 + '"'
         attribute_operation            = 'operation="'            + str(elem_nf.get('operation'))            + '"'
         attribute_freq_op              = 'freq_op="'              + str(elem_nf.get('freq_op'))              + '"'
         attribute_freq_offset          = 'freq_offset="'          + str(elem_nf.get('freq_offset'))          + '"'
         attribute_expr                 = 'expr="'                 + str(elem_nf.get('expr'))                 + '"'
         attribute_detect_missing_value = 'detect_missing_value="' + str(elem_nf.get('detect_missing_value')) + '"'
         attribute_prec                 = 'prec="'                 + str(elem_nf.get('prec'))                 + '"'
         attribute_read_access          = 'read_access="'          + str(elem_nf.get('read_access'))          + '"'
         attribute_standard_name        = 'standard_name="'        + str(elem_nf.get('standard_name'))        + '"'
         attribute_long_name            = 'long_name="'            + str(elem_nf.get('long_name'))            + '"'
         attribute_comment              = 'comment="'              + str(elem_nf.get('comment'))              + '"'

         if True:
          # Omit all attributes with the value "None":
          if attribute_id                  [-7:] == '="None"': attribute_id                   = ''
          if attribute_field_ref           [-7:] == '="None"': attribute_field_ref            = ''
          if attribute_enabled             [-7:] == '="None"': attribute_enabled              = ''
          if attribute_unit                [-7:] == '="None"': attribute_unit                 = ''
          if attribute_grid_ref            [-7:] == '="None"': attribute_grid_ref             = ''
          if attribute_axis_ref            [-7:] == '="None"': attribute_axis_ref             = ''
          if attribute_name                [-7:] == '="None"': attribute_name                 = ''
          if attribute_operation           [-7:] == '="None"': attribute_operation            = ''
          if attribute_freq_op             [-7:] == '="None"': attribute_freq_op              = ''
          if attribute_freq_offset         [-7:] == '="None"': attribute_freq_offset          = ''
          if attribute_expr                [-7:] == '="None"': attribute_expr                 = ''
          if attribute_detect_missing_value[-7:] == '="None"': attribute_detect_missing_value = ''
          if attribute_prec                [-7:] == '="None"': attribute_prec                 = ''
          if attribute_read_access         [-7:] == '="None"': attribute_read_access          = ''
          if attribute_standard_name       [-7:] == '="None"': attribute_standard_name        = ''
          if attribute_long_name           [-7:] == '="None"': attribute_long_name            = ''
          if attribute_comment             [-7:] == '="None"': attribute_comment              = ''

         for attribute in elem_nf.attrib:
          if attribute not in ['id', 'field_ref', 'enabled', 'unit', 'grid_ref', 'axis_ref', 'name', 'operation', 'freq_op', 'freq_offset', 'expr', 'detect_missing_value', 'prec', 'read_access', 'standard_name', 'long_name', 'comment']:
           print(' WARNING: attribute missed: {} tag={}'.format(attribute, elem_nf.tag))
         ecearth_field_def_nf.write(' {:31} {:40} {:17} {:25} {:42} {:18} {:40} {:20} {:18} {:22} {:50} {:31} {:9} {:19}{:99} {:102} {:58}' \
                                    .format(attribute_id                  , \
                                            attribute_field_ref           , \
                                            attribute_enabled             , \
                                            attribute_unit                , \
                                            attribute_grid_ref            , \
                                            attribute_axis_ref            , \
                                            attribute_name                , \
                                            attribute_operation           , \
                                            attribute_freq_op             , \
                                            attribute_freq_offset         , \
                                            attribute_expr                , \
                                            attribute_detect_missing_value, \
                                            attribute_prec                , \
                                            attribute_read_access         , \
                                            attribute_standard_name       , \
                                            attribute_long_name           , \
                                            attribute_comment             ))
        else:
         ecearth_field_def_nf.write('{}<{}'.format(indentation, elem_nf.tag))
         for attribute in elem_nf.attrib:
          ecearth_field_def_nf.write(' {:}="{:}"'.format(attribute, elem_nf.get(attribute)))
         ecearth_field_def_nf.write('>\n')

       elif event == 'end':
        # Add the tag closings:
        indentation = ' ' * 2 * (len(tag_path) - 1)
       #print(' end:   event = {:7} element = {}'.format(event, elem_nf.tag))
        if elem_nf.tag == 'field':
         ecearth_field_def_nf.write('> </{}>\n'.format(elem_nf.tag))
        else:
         ecearth_field_def_nf.write('{}</{}>\n'.format(indentation, elem_nf.tag))
        tag_path.pop()

  # Test the XML syntax by reading the just created ecearth_field_def_nf_file:
  tree_ecearth_field_def_nf = ET.parse(ecearth_field_def_nf_filename)
  root_ecearth_field_def_nf = tree_ecearth_field_def_nf.getroot()


 if True:
  print_next_step_message(6, 'Checking the field elements by using the combined field_def file')

  # Duplicate checking on field attributes:
  tags = ['field', 'field_group']
  for tag in tags:

   recorded_ids            = []
  #recorded_field_refs     = []
   recorded_names          = []
   duplicated_ids          = []
   duplicated_names        = []
   field_refs_with_id      = {} # dictionary
   field_refs_with_name    = {} # dictionary
   field_refs_without_name = []

   xpath_expression = ".//" + tag

   # Check whether there are duplicate id's or duplicate field_ref cases:
   i = 0
  #for element in root_ecearth_field_def_nf.findall(xpath_expression):
   for element in root_main.findall(xpath_expression):
    i += 1

    if element.get('id'):
     # Select all field elements with an id attribute
     if element.get('id') in recorded_ids:
      duplicated_ids.append(element.get('id'))
     #print(' WARNING: Duplicate {:12} id: {}'.format(tag, element.get('id')))
     else:
      recorded_ids.append(element.get('id'))

    if element.get('field_ref'):
     # Select all field elements with a field_ref attribute
    #if element.get('field_ref') in recorded_field_refs:
    # pass
    #else:
    # recorded_field_refs.append(element.get('field_ref'))
     if element.get('id'):
      field_refs_with_id[element.get('field_ref')] = element.get('id')
     if element.get('name'):
      field_refs_with_name[element.get('field_ref')] = element.get('name')
     else:
      field_refs_without_name.append(element.get('field_ref'))

    if element.get('name'):
     # Select all field elements with a name attribute
     if element.get('name') in recorded_names:
      duplicated_names.append(element.get('name'))
     #print(' WARNING: Duplicate {:12} name: {}'.format(tag, element.get('name')))
     else:
      recorded_names.append(element.get('name'))

   print('\n WARNING: Duplicate {:12} id        attributes: {}\n'.format(tag, sorted(set(duplicated_ids))))
  #print('\n          Recorded  {:12} id        attributes: {}\n'.format(tag, sorted(set(recorded_ids))))
  #print(  '          Recorded  {:12} field_ref attributes: {}\n'.format(tag, sorted(set(recorded_field_refs))))
   print(  ' WARNING: Duplicate {:12} name      attributes: {}\n'.format(tag, sorted(set(duplicated_names))))
   print(  ' WARNING: {} {:12} elements with a field_ref but without a name {}\n'.format(len(sorted(set(field_refs_without_name))), tag, sorted(set(field_refs_without_name))))

   if len(field_refs_with_id) > 0:
    print('\n The {} elements with a field_ref attribute which also have an id attribute:'.format(tag))
    print('  {:37} {}'.format('field_ref', 'id'))
    for key, value in field_refs_with_id.items():
     print('  {:37} {}'.format(key, value))
    print()
   if False:
    if len(field_refs_with_name) > 0:
     print('\n The {} elements with a field_ref attribute which also have a name attribute:'.format(tag))
     print('  {:37} {}'.format('field_ref', 'name'))
     for key, value in field_refs_with_name.items():
      print('  {:37} {}'.format(key, value))
     print()

   print(' In total we have {:3} {} elements'.format(i, tag))
   print('  {:3} of them have both a field_ref and an id   attribute'.format(len(field_refs_with_id)))
   print('  {:3} of them have both a field_ref and a  name attribute'.format(len(field_refs_with_name)))
   print('  {:3} of them have      a field_ref but no name attribute ({} of them have a different field_ref value)'.format(len(field_refs_without_name), len(set(field_refs_without_name))))
   print('  {:3} of them have a duplicate id   attribute'.format(len(duplicated_ids)))
   print('  {:3} of them have a duplicate name attribute\n'.format(len(duplicated_names)))

  # Check which list of attributes are part of the field elements and of the two field_group elements levels:
  tags = ['.//field', './ecearth4_nemo_field_definition/field_definition/field_group', './ecearth4_nemo_field_definition/field_definition/field_group/field_group']
  for tag in tags:

   list_of_attributes = []
   xpath_expression = tag
   print(' Overview of attributes which occur at least one time within the xpath search: {}'.format(xpath_expression))
   for element in root_main.findall(xpath_expression):
    for attribute in element.attrib.keys():
     list_of_attributes.append(attribute)
   print(' {}\n'.format(sorted(list(set(list_of_attributes)))))


  def check_attribute_occurence(attribute_list, xpath_expression, info):
      # Check how many tags have a certain attribute:
      for att in attribute_list:
       i_1 = 0
       i_2 = 0
       for element in root_main.findall(xpath_expression):
        if att in element.attrib.keys():
         i_1 += 1
        else:
         i_2 += 1
       print(' The {:25} is available in {:4} {} elements{} and {:4} times this is not the case.'.format(att, i_1, element.tag, info, i_2))
      print()

  attribute_list_for_field_elements                 =  ['axis_ref'                 , \
                                                        'comment'                  , \
                                                        'detect_missing_value'     , \
                                                        'enabled'                  , \
                                                        'expr'                     , \
                                                        'field_ref'                , \
                                                        'freq_offset'              , \
                                                        'freq_op'                  , \
                                                        'grid_ref'                 , \
                                                        'id'                       , \
                                                        'long_name'                , \
                                                        'name'                     , \
                                                        'operation'                , \
                                                        'prec'                     , \
                                                        'read_access'              , \
                                                        'standard_name'            , \
                                                        'unit'                       \
                                                       ]

  attribute_list_for_field_group_elements_of_level_1 = ['chunking_blocksize_target', \
                                                        'grid_ref'                 , \
                                                        'id'                         \
                                                       ]

  attribute_list_for_field_group_elements_of_level_2 = ['domain_ref'               , \
                                                        'enabled'                  , \
                                                        'grid_ref'                 , \
                                                        'id'                       , \
                                                        'operation'                  \
                                                       ]

  check_attribute_occurence(attribute_list_for_field_elements                 , './/field'                                                                 , '')
  check_attribute_occurence(attribute_list_for_field_group_elements_of_level_1, './ecearth4_nemo_field_definition/field_definition/field_group'            , ' (level 1)')
  check_attribute_occurence(attribute_list_for_field_group_elements_of_level_2, './ecearth4_nemo_field_definition/field_definition/field_group/field_group', ' (level 2)')
  print()



  # Inherit field element properties (i.e. attributes) via field_def references (the ambiguity check):

  i    = 0
  i_fr = 0

  xpath_path       = ".//field"                              # Looping over all field elements in any layer
  xpath_expression = xpath_path
 #xpath_expression = xpath_path + "[@" + selected_attribute + "]"

  for element in root_main.findall(xpath_expression):
   i += 1

   if element.get('field_ref'):
    # Select all field elements with a field_ref
    i_fr += 1

    # Check whether the field_ref has a unique match with one field id (remember our check that any field has either a field_ref attribute or an id attribute, some have both):
    list_of_matching_ids_with_field_ref = []
    for elem in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]'):
     # Check whether there are multiple matching id's for a given field_ref, collect each match in the list below:
     list_of_matching_ids_with_field_ref.append(elem)

    # Check whether a correct unique id match is detected for a given field_ref:
    if   len(list_of_matching_ids_with_field_ref) == 1:
     pass
    #print(' For {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) the id {} is detected with attributes: {}'.format(element.tag, i, element.get('field_ref'), i_fr, list_of_matching_ids_with_field_ref[0].attrib['id'], elem.attrib))
    elif len(list_of_matching_ids_with_field_ref) == 0:
     print(' ERROR: For {} element {:3} with field_ref {:27} no field id in any of the field_def files is found'.format(element.tag, i, element.get('field_ref')))
    else:
     print(' ERROR: For {} element {:3} with field_ref {:27} multiple field id {} with grid_ref {} are detected, which leads to an ambiguity'.format(element.tag, i, element.get('field_ref'), [x.get('id') for x in list_of_matching_ids_with_field_ref], [x.get('grid_ref') for x in list_of_matching_ids_with_field_ref]))
     # The current catch here (spaces changed for the one with captitals) is:
     #  <field id="ttrd_evd_li" long_name="layer integrated heat-trend: evd convection " unit="W/m^2">ttrd_evd_e3t * 1026.0 * 3991.86795711963  </field>
     #  <field id="ttrd_evd_li" long_name="layer integrated heat-trend: EVD convection " unit="W/m^2">ttrd_evd_e3t * 1026.0 * 3991.86795711963  </field>
     #  <field id="strd_evd_li" long_name="layer integrated salt-trend: evd convection " unit="kg/(m^2 s)"> strd_evd_e3t * 1026.0 * 0.001  </field>
     #  <field id="strd_evd_li" long_name="layer integrated salt-trend: EVD convection " unit="kg/(m^2 s)"> strd_evd_e3t * 1026.0 * 0.001  </field>
  print('\n')


  # Inherit field element properties (i.e. attributes) via field_def references:

  def inherit_message(attribute, ancestor_element, element, i, i_fr, ancestor_label):
      print(' The {:11} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) {:25} {:30} a {:11} attribute: {:29} id: {:27} name: {:20} standard_name: {:15} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, ancestor_label, ancestor_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('name')), str(element.get('standard_name')), str(element.get('long_name'))))

  def id_inherit_message(attribute, ancestor_element, element, i, ancestor_label):
      print(' The {:11} element {:4} with id        attribute: {:27}              {:25} {:30} a {:11} attribute: {:29} id: {:27} name: {:20} standard_name: {:15} long_name: {}'.format(element.tag, i, element.get('id')              , ancestor_label, ancestor_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('name')), str(element.get('standard_name')), str(element.get('long_name'))))

  def print_reference_chain(chain_of_reference):
       chain = ' Id: {:20} '.format(chain_of_reference[0])
       for string in chain_of_reference[1:]:
        chain += ' => {:20}'.format(string)
       return chain

  def find_referenced_element(starting_element, chain_of_reference):
      # A starting_element is taken and it is checked whether this element has a field_ref attribute. If so a recursive check is carried out for this element.
      for referenced_element in root_main.findall('.//field[@id="'+starting_element.get('field_ref')+'"]'):
       if referenced_element.get('field_ref'):
          chain_of_reference.append(referenced_element.get('field_ref'))
          print(' WARNING: The detected field_ref {:20} is pointing itself as well to another field_ref {:20} {}'.format(starting_element.get('field_ref'), referenced_element.get('field_ref'), print_reference_chain(chain_of_reference)))
          find_referenced_element(referenced_element, chain_of_reference)


  xpath_path       = ".//field"                              # Looping over all field elements in any layer
  xpath_expression = xpath_path
 #xpath_expression = xpath_path + "[@" + selected_attribute + "]"

 #for attribute in ['grid_ref', 'operation', 'domain_ref']:
 #for attribute in ['grid_ref', 'operation', 'unit', 'freq_offset']:
  i    = 0
  i_fr = 0

  for element in root_main.findall(xpath_expression):
   i += 1

   if element.get('field_ref'):
    # Select all field elements with a field_ref
    # Inherit the attribute via the field_ref element (directly or from its parent, grand parent, etc) if applicable:
    i_fr += 1
    print()


    if True:
     # The chain of references contains on the very first element the id of the starting element, thereafter in the recursive function the field_ref's
     # are added one by one in case more references are detected.
     chain_of_reference = [element.get('id'), element.get('field_ref')]
     find_referenced_element(element, chain_of_reference)


    if False:
     # Check whether the field_ref field itself also points to a field_ref:
     # So far this is only the check, no further change due to any inherit decission is made here yet (when a references or even a chain of references are detected).
     for element_ref_level_1 in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]'):
      if element_ref_level_1.get('field_ref'):
         print(' WARNING 1: The detected 1st level field_ref is pointing itself to a 2nd level field_ref as well for: via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref')))

         # Check whether the second level field_ref field itself also points again to another field_ref:
         for element_ref_level_2 in root_main.findall('.//field[@id="'+element_ref_level_1.get('field_ref')+'"]'):
          if element_ref_level_2.get('field_ref'):
             print(' WARNING 2: The detected 2nd level field_ref is pointing itself to a 3rd level field_ref as well for: {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref')))

             # Check whether the third level field_ref field itself also points again to another field_ref:
             for element_ref_level_3 in root_main.findall('.//field[@id="'+element_ref_level_2.get('field_ref')+'"]'):
              if element_ref_level_3.get('field_ref'):
                 print(' WARNING 3: The detected 3rd level field_ref is pointing itself to a 4th level field_ref as well for: {} via {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref'), element_ref_level_3.get('field_ref')))

                 # Check whether the third level field_ref field itself also points again to another field_ref:
                 for element_ref_level_4 in root_main.findall('.//field[@id="'+element_ref_level_3.get('field_ref')+'"]'):
                  if element_ref_level_4.get('field_ref'):
                     print(' WARNING 4: The detected 4th level field_ref is pointing itself to a 5th level field_ref as well for: {} via {} via {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref'), element_ref_level_3.get('field_ref'), element_ref_level_4.get('field_ref')))

                     # Check whether the third level field_ref field itself also points again to another field_ref:
                     for element_ref_level_5 in root_main.findall('.//field[@id="'+element_ref_level_4.get('field_ref')+'"]'):
                      if element_ref_level_5.get('field_ref'):
                         print(' WARNING 5: The detected 5th level field_ref is pointing itself to a 6th level field_ref as well for: {} via {} via {} via {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref'), element_ref_level_3.get('field_ref'), element_ref_level_4.get('field_ref'), element_ref_level_5.get('field_ref')))

                         # Check whether the third level field_ref field itself also points again to another field_ref:
                         for element_ref_level_6 in root_main.findall('.//field[@id="'+element_ref_level_5.get('field_ref')+'"]'):
                          if element_ref_level_6.get('field_ref'):
                             print(' WARNING 6: The detected 6th level field_ref is pointing itself to a 7th level field_ref as well for: {} via {} via {} via {} via {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref'), element_ref_level_3.get('field_ref'), element_ref_level_4.get('field_ref'), element_ref_level_5.get('field_ref'), element_ref_level_6.get('field_ref')))

                             # Check whether the third level field_ref field itself also points again to another field_ref:
                             for element_ref_level_7 in root_main.findall('.//field[@id="'+element_ref_level_6.get('field_ref')+'"]'):
                              if element_ref_level_7.get('field_ref'):
                                 print(' WARNING 7: The detected 7th level field_ref is pointing itself to a 8th level field_ref as well for: {} via {} via {} via {} via {} via {} to  {}'.format(element.get('field_ref'), element_ref_level_1.get('field_ref'), element_ref_level_2.get('field_ref'), element_ref_level_3.get('field_ref'), element_ref_level_4.get('field_ref'), element_ref_level_5.get('field_ref'), element_ref_level_6.get('field_ref'), element_ref_level_7.get('field_ref')))


    for attribute in ['grid_ref', 'operation', 'unit', 'freq_offset']:

      # Inherit attribute if applicable:
      if element.get(attribute):
                   inherit_message(attribute,                 element, element, i, i_fr, 'has for                             ')
      else:
       for field_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]'):
        if field_element.get(attribute):
                   # Inherit the attribute from the field which matched with the field_ref field:
                   element.set(attribute, field_element.get(attribute))
                   inherit_message(attribute,           field_element, element, i, i_fr, 'inherits from              field_ref')
        else:
         # For those field elements which do not have the attribute in their direct attribute list: Search for the attribute within the attribute list of the parent of the field_ref field:
         for parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]...'):
          if parent_element.get(attribute):
                   # Inherit the attribute from the parent of the field which matched with the field_ref field:
                   element.set(attribute, parent_element.get(attribute))
                   inherit_message(attribute,          parent_element, element, i, i_fr, 'inherits from                 parent')
          else:
           # For those field elements which neither have the attribute in their direct attribute list or in the attribute list of their parent: Searchzs for the attribute within the attribute list of the grand parent of the field_ref field:
           for grand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../...'):
            if grand_parent_element.get(attribute):
                   # Inherit the attribute from the grand parent of the field which matched with the field_ref field:
                   element.set(attribute, grand_parent_element.get(attribute))
                   inherit_message(attribute,    grand_parent_element, element, i, i_fr, 'inherits from           grand parent')
            else:
             for ggrand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../.../...'):
              if ggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand parent of the field which matched with the field_ref field:
                   element.set(attribute, ggrand_parent_element.get(attribute))
                   inherit_message(attribute,   ggrand_parent_element, element, i, i_fr, 'inherits from          ggrand parent')
              else:
               for gggrand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../.../.../...'):
                if gggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand grand parent of the field which matched with the field_ref field:
                   element.set(attribute, gggrand_parent_element.get(attribute))
                   inherit_message(attribute,  gggrand_parent_element, element, i, i_fr, 'inherits from         gggrand parent')
                else:
                 for ggggrand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../.../.../.../...'):
                  if ggggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand grand grand parent of the field which matched with the field_ref field:
                   element.set(attribute, ggggrand_parent_element.get(attribute))
                   inherit_message(attribute, ggggrand_parent_element, element, i, i_fr, 'inherits from        ggggrand parent')
                  else:
                   inherit_message(attribute, ggggrand_parent_element, element, i, i_fr, 'no inheritance up to                ')


   elif element.get('id'):
    # Select all field elements without a field_ref (they should all have an id attribute):

    print()

    for attribute in ['grid_ref', 'operation', 'unit', 'freq_offset']:

     if element.get(attribute):
                   id_inherit_message(attribute,                 element, element, i, 'has for                             ')
     else:
         # For those field elements which do not have the attribute in their direct attribute list: Search for the attribute within the attribute list of their parent:
         for parent_element in root_main.findall('.//field[@id="'+element.get('id')+'"]...'):
          if parent_element.get(attribute):
                   # Inherit the attribute from their parent:
                   element.set(attribute, parent_element.get(attribute))
                   id_inherit_message(attribute,          parent_element, element, i, 'inherits from                 parent')
          else:
           # For those field elements which neither have the attribute in their direct attribute list or in the attribute list of their parent: Searchzs for the attribute within the attribute list of the grand parent:
           for grand_parent_element in root_main.findall('.//field[@id="'+element.get('id')+'"].../...'):
            if grand_parent_element.get(attribute):
                   # Inherit the attribute from the grand parent:
                   element.set(attribute, grand_parent_element.get(attribute))
                   id_inherit_message(attribute,    grand_parent_element, element, i, 'inherits from           grand parent')
            else:
             for ggrand_parent_element in root_main.findall('.//field[@id="'+element.get('id')+'"].../.../...'):
              if ggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand parent:
                   element.set(attribute, ggrand_parent_element.get(attribute))
                   id_inherit_message(attribute,   ggrand_parent_element, element, i, 'inherits from          ggrand parent')
              else:
               for gggrand_parent_element in root_main.findall('.//field[@id="'+element.get('id')+'"].../.../.../...'):
                if gggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand grand parent:
                   element.set(attribute, gggrand_parent_element.get(attribute))
                   id_inherit_message(attribute,  gggrand_parent_element, element, i, 'inherits from         gggrand parent')
                else:
                 for ggggrand_parent_element in root_main.findall('.//field[@id="'+element.get('id')+'"].../.../.../.../...'):
                  if ggggrand_parent_element.get(attribute):
                   # Inherit the attribute from the grand grand grand grand parent:
                   element.set(attribute, ggggrand_parent_element.get(attribute))
                   id_inherit_message(attribute, ggggrand_parent_element, element, i, 'inherits from        ggggrand parent')
                  else:
                   id_inherit_message(attribute, ggggrand_parent_element, element, i, 'no inheritance up to                ')

   else:
    print(' ERROR: The element {} {:3} has no id & no field_ref attribute. This should not occur. Detected attributes: {}'.format(element.tag, i, element.attrib))

  print()



# inherit before: unit, freq_offset, grid_ref;  add: id, text


# From the basic flat ece4 file_def file, giving an idea which attributes were expkicitly taken to the file_def file
#   <file id="file8" name_suffix="_opa_grid_T_2D" output_freq="3h">

#    <field id="id_3h_tos"                                      # id_<cmip6 var name>_<cmip6 table name>
#           name="tos"                                          # <cmip6 var name>
#           table="3hr"                                         # <cmip6 table name>
#           field_ref="sst_pot"
#           grid_ref="grid_T_2D"
#           unit="degC"
#           enabled="False"
#           operation="instant"
#           freq_op="3h"   >                                                                        </field>

#   </file>


if __name__ == '__main__':
    main()
