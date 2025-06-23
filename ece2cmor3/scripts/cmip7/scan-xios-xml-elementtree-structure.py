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

  ecearth_field_def_file = 'ec-earth-definition.xml'


  new_root = ET.Element('ecearth_field_definition')
  ET.SubElement(new_root, 'ecearth4_nemo_field_definition')
  ET.SubElement(new_root, 'ecearth4_oifs_field_definition')
  ET.SubElement(new_root, 'ecearth4_lpjg_field_definition')

  ET.indent(new_root, space='  ')
  ET.dump(new_root)

 # I am not able to create a new_root_tree from the new_root and therefore I am not able to write it to a
 # file and/or to continue extending this tree. There fore manually creating a file with this content abd reading it in.
 #new_root_tree = ET.TreeBuilder(new_root)
 #new_root_tree = ET.parse(new_root)
 #new_root.write('new-root.xml')
 #new_root.ET.write('new-root.xml')
 #new_root_tree.write('new-root.xml')

  # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
 #with open("ec-earth-definition-canonicalized.xml", mode='w', encoding='utf-8') as out_file:
 # ET.canonicalize(from_file= ecearth_field_def_file, with_comments=True, out=out_file)


  pf = os.path.split(ecearth_field_def_file)
  print('\n\n {}\n'.format(pf[1]))

  # Load the xml file:
  tree_main = ET.parse(ecearth_field_def_file)
  root_main = tree_main.getroot()
 #print(' {} {}'.format(root_main.tag, root_main.attrib))


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
  tree_main.write('test.xml')

  # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
  with open("test-canonicalized.xml", mode='w', encoding='utf-8') as out_file:
   ET.canonicalize(from_file="test.xml", with_comments=True, out=out_file)


if __name__ == '__main__':
    main()
