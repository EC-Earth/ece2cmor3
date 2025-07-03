#!/usr/bin/env python3
"""

 Scanning the XML structure of a set of XIOS file_def files:

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

 field_def_file_collection = [field_def_file_inn, \
                              field_def_file_pis, \
                              field_def_file_ice, \
                              field_def_file_oce  \
                             ]

 if True:
  # Scan the field_def file stucture, how many layers (child, grandchild and so on). If field_group and field
  # are defined at the same level. If within a field_group another field_group is defined. Check for other tags
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
     print(' level 1: {}'.format(child.tag))
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
      print(' level 2: {}'.format(grandchild.tag))
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
       print(' level 3: {}'.format(ggrandchild.tag))
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
        print(' level 4: {}'.format(gggrandchild.tag))
   print('                        Number of field is {:3} & number of field_group is {:3} for level 4'.format(i, j))



 if True:
  # Show for a certain xpath expression for a certain selected attribute for a certain xpath path which elements are selected:
  print_next_step_message(2, 'Show the selected elements for a certain xpath expression')

  selected_attribute = 'field_ref'
  selected_attribute = 'id'
 #xpath_path         = "./field_group/field_group/"            # Looping over only the field_group elements in the field_group/field_group/       layer
 #xpath_path         = "./field_group/"                        # Looping over only the field_group elements in the field_group/                   layer
 #xpath_path         = ".//field_group"                        # Looping over all      field_group elements in any                                layer
 #xpath_path         = "./field_group/field_group/field/"      # Looping over only the field       elements in the field_group/field_group/field/ layer
 #xpath_path         = "./field_group/field/"                  # Looping over only the field       elements in the field_group/                   layer
  xpath_path         = "./field/"                              # Looping over only the field       elements in the field                          layer  id: agrif_spf, ahmf_2d, ahmf_3d
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
  # Loop over all field elements at all levels and check whether they have at least a field_ref or an id. And count the number of field elements.
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

    # For every field element either an id or a field_ref attribute is present in all field elements in all field_def files.
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
  # Loop over all field elements at all levels and check whether they have at least a field_ref or an id. And count the number of field elements.
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
    # In a few cfieases when a field_ref attribute is present an id attribute is specified as well in the ld_def files for a field element.
    i_f            = 0  # The number of field elements
    i_fr           = 0  # The number of field elements with    a field_ref attribute
    i_no_fr        = 0  # The number of field elements without a field_ref attribute
    i_fr_and_id    = 0  # The number of field elements with    a field_ref attribute and an id attribute
    i_fr_and_gr    = 0  # The number of field elements with    a field_ref attribute and a  grid_ref attribute
    i_no_fr_and_gr = 0  # The number of field elements without a field_ref attribute and a  grid_ref attribute
    for element in root.findall(xpath_expression):
     i_f += 1
     if element.get('field_ref'):
      # The field elements with a field_ref attribute (some have an id attribute as well)
      i_fr += 1
      if element.get('id'):
       i_fr_and_id += 1
       if verbose_level >  0: print(' A {} element has a field_ref {:27} and an id {}'.format(element.tag, element.get('field_ref'), element.get('id')))
      else:
       if verbose_level >  0: print(' A {} element has a field_ref {:27}'             .format(element.tag, element.get('field_ref')))


      # Check for grid_ref attribute in case a field_ref attribute is available:
      if element.get('grid_ref'):
       i_fr_and_gr += 1
       if verbose_level >  0: print(' A {} element has a field_ref {:27} and a grid_ref {}'.format(element.tag, element.get('field_ref'), element.get('grid_ref')))
      else:
       if verbose_level >  0: print(' A {} element has a field_ref {:27} but no grid_ref'  .format(element.tag, element.get('field_ref')))

     else:
      # The field elements without a field_ref attribute, they all have an id attribute:
      i_no_fr += 1
      if element.get('id'):
       if verbose_level >  1: print(' A {} element has an id {:27} but no field_ref attribute'.format(element.tag, element.get('id')))
      else:
       if verbose_level == 1: print(' ERROR: A {} element has no id attribute and no field_ref attribute. This should not occur!'.format(element.tag))

      # Check for grid_ref attribute in case no field_ref attribute is available:
      if element.get('grid_ref'):
       i_no_fr_and_gr += 1
       if verbose_level >  0: print(' A {} element has no field_ref but an id {:27} and a  grid_ref {}'.format(element.tag, element.get('id'), element.get('grid_ref')))
      else:
       if verbose_level >  0: print(' A {} element has no field_ref but an id {:27} but no grid_ref'   .format(element.tag, element.get('id')))



    print(' {:4} {:12} elements with a field_ref attribute and {:3} with a grid_def attribute as well in the field_def file {}'.format(i_fr, element.tag, i_fr_and_gr, pf[1]))
    i_total_fr           = i_total_fr           + i_fr
    i_total_no_fr        = i_total_no_fr        + i_no_fr
    i_total_fr_and_id    = i_total_fr_and_id    + i_fr_and_id
    i_total_fr_and_gr    = i_total_fr_and_gr    + i_fr_and_gr
    i_total_no_fr_and_gr = i_total_no_fr_and_gr + i_no_fr_and_gr

   print('\n {:4} {:12} elements with a  field_ref attribute in all the field_def files and {:3} of them have an id       attribute as well.'  .format(i_total_fr   , element.tag, i_total_fr_and_id))
   print(  ' {:4} {:12} elements with a  field_ref attribute in all the field_def files and {:3} of them have a  grid_ref attribute as well.'  .format(i_total_fr   , element.tag, i_total_fr_and_gr))
   print(  ' {:4} {:12} elements with no field_ref attribute in all the field_def files and {:3} of them have a  grid_ref attribute as well.\n'.format(i_total_no_fr, element.tag, i_total_no_fr_and_gr))



 if True:
  print_next_step_message(5, 'Combine the field_def files')

  ecearth_field_def_file         = 'ec-earth-definition.xml'           # The one which is not canonicalized
  ecearth_field_def_file_canonic = 'ec-earth-definition-canonic.xml'   # The one which is     canonicalized


  # Create the basic mian structure which will be populated with the elements of the various field_def files later on:
  root_main = ET.Element('ecearth_field_definition')
  ET.SubElement(root_main, 'ecearth4_nemo_field_definition')
  ET.SubElement(root_main, 'ecearth4_oifs_field_definition')
  ET.SubElement(root_main, 'ecearth4_lpjg_field_definition')
  ET.indent(root_main, space='  ')
 #ET.dump(root_main)

  # Create the tree object for the fresh created root for our main structure:
  tree_main = ET.ElementTree(root_main)

  if False:
   # The xml file with the basic structure can be optionally written:
   ecearth_field_def_file_tmp = 'ec-earth-main-structure-tmp.xml'  # The one which is not canonicalized
   ecearth_field_def_file     = 'ec-earth-main-structure.xml'      # The one which is     canonicalized

   # Write the basic xml structure to a file:
   tree_main.write(ecearth_field_def_file_tmp)
   # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
   with open(ecearth_field_def_file, mode='w', encoding='utf-8') as out_file:
    ET.canonicalize(from_file=ecearth_field_def_file_tmp, with_comments=True, out=out_file)

   if False:
    # And optionally read the basic main structure from this file:
    pf = os.path.split(ecearth_field_def_file)
    print('\n\n {}\n'.format(pf[1]))

    # Load the xml file:
    tree_main = ET.parse(ecearth_field_def_file)
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

   # Append the root element of each field_def file to the level of ecearth4_nemo_field_definition in the new field_def file:
   for element in root_main.findall(".//ecearth4_nemo_field_definition"):
    element.append(root)

  # For neat indentation, but also for circumventing the newline trouble:
  ET.indent(tree_main, space='  ')

  # Writing the combined result to a new xml file:
  tree_main.write(ecearth_field_def_file)

  # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
  with open(ecearth_field_def_file_canonic, mode='w', encoding='utf-8') as out_file:
   ET.canonicalize(from_file=ecearth_field_def_file, with_comments=True, out=out_file)



 if True:
  print_next_step_message(6, 'Checking the field elements by using the combined field_def files')

  # Duplicate checking on field attributes:
  tags = ['field', 'field_group']
  for tag in tags:

   recorded_ids            = []
   recorded_field_refs     = []
   recorded_names          = []
   duplicated_ids          = []
   duplicated_field_refs   = []
   duplicated_names        = []
   field_refs_with_id      = {}
   field_refs_with_name    = {}
   field_refs_without_name = []

   xpath_expression = ".//" + tag

   # Check whether there are duplicate id's or duplicate field_ref cases:
   i = 0
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
     # Select all field elements with an field_ref attribute
     if element.get('field_ref') in recorded_field_refs:
      duplicated_field_refs.append(element.get('field_ref'))
     #print(' WARNING: Duplicate {:12} field_ref: {}'.format(tag, element.get('field_ref')))
     else:
      recorded_field_refs.append(element.get('field_ref'))
     if element.get('id'):
      field_refs_with_id[element.get('field_ref')] = element.get('id')
     if element.get('name'):
      field_refs_with_name[element.get('field_ref')] = element.get('name')
     else:
      field_refs_without_name.append(element.get('field_ref'))

    if element.get('name'):
     # Select all field elements with an name attribute
     if element.get('name') in recorded_names:
      duplicated_names.append(element.get('name'))
     #print(' WARNING: Duplicate {:12} name: {}'.format(tag, element.get('name')))
     else:
      recorded_names.append(element.get('name'))

   if True : print('\n WARNING: Duplicate {:12} id        attributes: {}\n'.format(tag, sorted(set(duplicated_ids))))
  #if True : print('\n WARNING: Recorded  {:12} id        attributes: {}\n'.format(tag, sorted(set(recorded_ids))))
   if False: print(  ' WARNING: Duplicate {:12} field_ref attributes: {}\n'.format(tag, sorted(set(duplicated_field_refs))))
   if True : print(  ' WARNING: Duplicate {:12} name      attributes: {}\n'.format(tag, sorted(set(duplicated_names))))
   if True : print(  ' WARNING: {:12} elements with a field_ref but without a name {}\n'.format(tag, sorted(set(field_refs_without_name))))

   if True:
    if len(field_refs_with_id) > 0:
     print('\n The {} field_ref elements which also have an id:'.format(tag))
     print('  {:37} {}'.format('field_ref', 'id'))
     for key, value in field_refs_with_id.items():
      print('  {:37} {}'.format(key, value))
     print()
   if False:
    if len(field_refs_with_name) > 0:
     print('\n The {} field_ref elements which also have a name:'.format(tag))
     print('  {:37} {}'.format('field_ref', 'name'))
     for key, value in field_refs_with_name.items():
      print('  {:37} {}'.format(key, value))
     print()

   print(' In total we have {:3} {} elements\n'.format(i, tag))



  # Check which list of attributes are part of the two field_group levels:
  tags = ['.//field', './ecearth4_nemo_field_definition/field_definition/field_group', './ecearth4_nemo_field_definition/field_definition/field_group/field_group']
  for tag in tags:

   list_of_attributes = []
   xpath_expression = tag
   print(' At least one time encountered attributes within the xpath search: {}'.format(xpath_expression))
   for element in root_main.findall(xpath_expression):
    for attribute in element.attrib.keys():
     list_of_attributes.append(attribute)
   print(' {}\n'.format(sorted(list(set(list_of_attributes)))))



  # Check how many tags have a certian attribute:
  for att in ['long_name', 'standard_name']:
   i_1 = 0
   i_2 = 0

   tags = ['.//field']
   for tag in tags:

    list_of_attributes = []
    xpath_expression = tag
   #print(' No {} for:'.format(att))
    for element in root_main.findall(xpath_expression):
     if att in element.attrib.keys():
      i_1 += 1
     else:
      i_2 += 1
     #print(' field_ref: {:27} id: {}'.format(str(element.get('field_ref')), str(element.get('id'))))
    print(' The {} is available in {} {} elements and {} times this is not the case.\n'.format(att, i_1, element.tag, i_2))



  # Inherit field element properties (i.e. attributes) via field_def references:

  def inherit_attribute_from_parent(loc_root, loc_element, attribute):
    # Inherit attribute from the parent of a field_ref field if applicable:
    if loc_element.get(attribute):
     # Select a field element with a field_ref and with the attribute:
     print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) with a    direct {:9} attribute: {}'.format(loc_element.tag, i, loc_element.get('field_ref'), i_fr, attribute, loc_element.get(attribute)))
    else:
     # For those field elements which do not have the direct attribute:  Find the attribute within the attribute list of the parent of the field_ref field:
     for elem in loc_root.findall('.//field[@id="'+loc_element.get('field_ref')+'"]...'):
      pass
     # Inheriting the attribute from the parent field_group which matched with the field_ref field:
     if elem.get(attribute):
      loc_element.set(attribute, elem.get(attribute))
      print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) with an indirect {:9} attribute: {}'.format(loc_element.tag, i, loc_element.get('field_ref'), i_fr, attribute, loc_element.get(attribute)))
    #else:
    # print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) has no  indirect {:9} attribute'    .format(loc_element.tag, i, loc_element.get('field_ref'), i_fr, attribute))

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

    if True:
     # Inherit attribute if applicable:
     for attribute in ['grid_ref']:
      if element.get(attribute):
               print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) has                                          an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
      else:
       for field_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]'):
        if field_element.get(attribute):
                 # Inherit the attribute from the parent of the field which matched with the field_ref field:
                 element.set(attribute, field_element.get(attribute))
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) inherits from     field_ref {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, field_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
        else:
         # For those field elements which do not have a direct operation attribute:  Find the operation within the attribute list of the parent of the field_ref field:
         for parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]...'):
          if parent_element.get(attribute):
                 # Inherit the attribute from the parent of the field which matched with the field_ref field:
                 element.set(attribute, parent_element.get(attribute))
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) inherits from        parent {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, parent_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
          else:
           for grand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../...'):
            if grand_parent_element.get(attribute):
                 # Inherit the attribute from the grand parent of the field which matched with the field_ref field:
                 element.set(attribute, grand_parent_element.get(attribute))
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) inherits from  grand parent {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, grand_parent_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
            else:
             for ggrand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../.../...'):
              if ggrand_parent_element.get(attribute):
                 # Inherit the attribute from the grand grand parent of the field which matched with the field_ref field:
                 element.set(attribute, ggrand_parent_element.get(attribute))
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) inherits from ggrand parent {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, ggrand_parent_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
              else:
               for gggrand_parent_element in root_main.findall('.//field[@id="'+element.get('field_ref')+'"].../.../.../...'):
                if gggrand_parent_element.get(attribute):
                 # Inherit the attribute from the grand grand grand parent of the field which matched with the field_ref field:
                 element.set(attribute, gggrand_parent_element.get(attribute))
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) inherits from gggrand parent {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, gggrand_parent_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))
                else:
                 print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) does not inherit up to level gggrand parent {:16} an {:11} attribute: {:30} id: {:27} long_name: {}'.format(element.tag, i, element.get('field_ref'), i_fr, gggrand_parent_element.tag, attribute, str(element.get(attribute)), str(element.get('id')), str(element.get('long_name'))))

#   inherit_attribute_from_parent(root_main, element, 'grid_ref')
   #inherit_attribute_from_parent(root_main, element, 'domain_ref')
#   inherit_attribute_from_parent(root_main, element, 'operation')
   #inherit_attribute_from_parent(root_main, element, 'unit')

    if False:
     # Inherit grid_ref attribute if applicable:
     if element.get('grid_ref'):
      # Select all field elements with a field_ref and with a grid_ref attribute:
      print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) with a    direct grid_ref  attribute: {}'.format(element.tag, i, element.get('field_ref'), i_fr, element.get('grid_ref')))
      pass
     else:
      # For those field elements which do not have a direct grid_ref attribute: Find the grid_ref within the attribute list of the parent of the field_ref field:
      for elem in root_main.findall('.//field[@id="'+element.get('field_ref')+'"]...'):
       # Inheriting the grid_ref from the parent field_group which matched with the field_ref field:
       element.set('grid_ref', elem.get('grid_ref'))
       print(' The {} element {:4} with field_ref attribute: {:27} (i_fr = {:3}) with an indirect grid_ref  attribute: {}'.format(element.tag, i, element.get('field_ref'), i_fr, element.get('grid_ref')))


   elif element.get('id'):
    # Select all field elements without a field_ref (they should all have an id attribute):
    pass
   else:
    print(' ERROR: The element {} {:3} has no id & no field_ref attribute. This should not occur. Detected attributes: {}'.format(element.tag, i, element.attrib))







#              if "unit" in elem.attrib:
#               detected_unit                    = elem.attrib["unit"]                  # Inheriting the unit        from the match with the field_ref field
#              else:
#               detected_unit                    = "no unit definition"
#              if "freq_offset" in elem.attrib:
#               detected_freq_offset             = elem.attrib["freq_offset"]           # Inheriting the freq_offset from the match with the field_ref field
#              else:
#               detected_freq_offset             = "no freq_offset"

#              if "unit" in roottree[group].attrib:
#               unit_elements.append(roottree[group].attrib["unit"])
#              else:
#               unit_elements.append(detected_unit)
#              if "freq_offset" in roottree[group].attrib:
#               freq_offset_elements.append(roottree[group].attrib["freq_offset"])
#              else:
#               freq_offset_elements.append(detected_freq_offset)

#              field_elements_attribute_1.append(roottree[group].attrib[attribute_1]) # Add the            id       of the considered element
#              field_elements_attribute_2.append('grid_ref="'+detected_grid_ref+'"')  # Add the inheriting grid_ref from the match with the field_ref field. Adding the attribute name itself as well
#              text_elements             .append(roottree[group].text)                # Add the            text     of the considered element

#              via_field_ref_message.append('                 {} {:2}                                        with id: {:35}     has a  grid_ref attribute: {:15} via the field_ref attribute: {:20} with unit: {}'.format(roottree[group].tag, group, roottree[group].attrib[attribute_1], detected_grid_ref, element.get('field_ref'), detected_unit))
#              if i_match > 1: print(' WARNING: Ambiguity because {:2} times an id is found which matches the field_ref {}'.format(i_match, element.get('field_ref')))




if __name__ == '__main__':
    main()
