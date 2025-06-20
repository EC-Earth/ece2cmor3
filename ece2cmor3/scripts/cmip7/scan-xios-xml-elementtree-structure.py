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
    print(' ####################################################################################')
    print(' ###  Test {:<2}:  {:63}   ###'.format(step, comment))
    print(' ####################################################################################\n')


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
     i = i + 1
    if child.tag == 'field_group':
     j = j + 1
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
      i = i + 1
     if grandchild.tag == 'field_group':
      j = j + 1
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
       i = i + 1
      if ggrandchild.tag == 'field_group':
       j = j + 1
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
        i = i + 1
       if gggrandchild.tag == 'field_group':
        j = j + 1
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

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(field_def_file)
   print('\n\n {}\n'.format(pf[1]))

   # Load the xml file:
   tree = ET.parse(field_def_file)
   root = tree.getroot()

   i = 0
   for element in root.findall(xpath_expression):
    i = i + 1
    print('{:4} {} {:25} {}'.format(i, element.tag, element.get(selected_attribute), element.attrib))



 if True:
  # Loop over all field elements at all levels and check whether they have at least a field_ref or an id. And count the number of field elements.
  print_next_step_message(3, 'Check if at least a field_ref or an id attribute is present')

  tags = ['field', 'field_group']
  for tag in tags:
   i_total = 0

   # Loop again over the various field_def files:
   for field_def_file in field_def_file_collection:

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(field_def_file)

    # Load the xml file:
    tree = ET.parse(field_def_file)
    root = tree.getroot()

    # For every field element either an id or a field_ref attribute is present in all field elements in all field_def files.
    # In a few cases when a field_ref attribute is present an id attribute is specified as well in the field_def files for a field element.
    i_f           = 0
    i_id_or_fr    = 0
    i_no_id_or_fr = 0
    xpath_expression = ".//" + tag
    for element in root.findall(xpath_expression):
     i_f = i_f + 1                           # Numbering the total amount of field elements
     if element.get('id') or element.get('field_ref'):
      i_id_or_fr = i_id_or_fr + 1
     else:
      i_no_id_or_fr = i_no_id_or_fr + 1
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
   i_total_fr        = 0
   i_total_fr_and_id = 0

   # Loop again over the various field_def files:
   for field_def_file in field_def_file_collection:

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(field_def_file)

    # Load the xml file:
    tree = ET.parse(field_def_file)
    root = tree.getroot()

    # For every field element either an id or a field_ref attribute is present in all field elements in all field_def files.
    # In a few cases when a field_ref attribute is present an id attribute is specified as well in the field_def files for a field element.
    i_f         = 0
    i_fr        = 0
    i_no_fr     = 0
    i_fr_and_id = 0
    xpath_expression = ".//" + tag
    for element in root.findall(xpath_expression):
     i_f = i_f + 1                           # Numbering the total amount of field elements
     if element.get('field_ref'):
      i_fr = i_fr + 1
      if element.get('id'):
       i_fr_and_id = i_fr_and_id + 1
       if verbose_level > 0: print(' A {} element has a field_ref {:27} and an id {}'.format(element.tag, element.get('field_ref'), element.get('id')))
      else:
       if verbose_level > 0: print(' A {} element has a field_ref {:27}'.format(element.tag, element.get('field_ref')))
     else:
      i_no_fr = i_no_fr + 1
      if element.get('id'):
       if verbose_level > 1: print(' A {} element has an id {:27} but no field_ref attribute'.format(element.tag, element.get('id')))
      else:
       if verbose_level > 1: print(' ERROR: A {} element has no id attribute and no field_ref attribute. This should not occur!'.format(element.tag))
    print(' {:4} {:12} elements with a field_ref attribute in the field_def file {}'.format(i_fr, element.tag, field_def_file))
    i_total_fr        = i_total_fr        + i_fr
    i_total_fr_and_id = i_total_fr_and_id + i_fr_and_id

   print('\n {:4} {:12} elements with a field_ref attribute in all the field_def files and {} of them have an id attribute as well.\n'.format(i_total_fr, element.tag, i_total_fr_and_id))











 if False:
  print_next_step_message(5, 'Grid_ref check - under construction')

  # Loop again over the various field_def files:
  for field_def_file in field_def_file_collection:

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(field_def_file)
   print('\n\n {}\n'.format(pf[1]))

   # Load the xml file:
   tree = ET.parse(field_def_file)
   root = tree.getroot()

   # For every field element either an id or a field_ref attribute is present in all field_def files.
   # If a field_ref is present than only sometimes an id is specified in the field_def files for a field element
   i_f  = 0
   i_id = 0
   i_fr = 0
   i_gr = 0
   for element in root.findall(".//field"):
    i_f = i_f + 1                           # Numbering the total amount of field elements
    if   element.get('id'):
     i_id = i_id + 1                        # Numbering the total amount of field elements with an id attribute
     # Check if any field element with an id attribute has  field_ref attribute:
     if element.get('field_ref'):
      print(' A {} element with an id {:27} does have a field_ref attribute {:27}, this situation has been detected in few cases!'.format(element.tag, element.get('id'), element.get('field_ref')))
    elif element.get('field_ref'):
     i_fr = i_fr + 1                        # Numbering the total amount of field elements with an field_ref attribute
     # Check if indeed any field element with a field_ref attribute has no id attribute:
     if element.get('id'):
      print(' A {} element with a field_ref {:27} does have an id attribute {:27}, this situation has not been detected before!'.format(element.tag, element.get('field_ref'), element.get('id')))
     else:
      pass
     #print(' A {} element with a field_ref {:27} does not have an id attribute'.format(element.tag, element.get('field_ref')))

     if element.get('grid_ref'):
      i_gr = i_gr + 1
     else:
      if element.get('field_ref'):
       print(' No grid_ref attribute and no field_ref attribute for field_ref = {}'.format(element.get('field_ref')))
      else:
       # Does not occur currently:
       print(' No grid_ref attribute and no field_ref attribute for id        = {}'.format(element.get('field_ref')))
    else:
     # This situation actually does not occur in the current ece4 field_def files.
     print('A {} element without an id and without a field_ref, this situation has not been detected before!'.format(element.tag))

   print('{:4} field tags have no id but do have a field_ref'.format(i_fr))

 #print(ET.dump(root))





  print_next_step_message(6, 'Combine sevaral field_def files - under construction')

  root = None


 # Load the xml file:
 root_1 = ET.parse(field_def_file_collection[0]).getroot()
 root_2 = ET.parse(field_def_file_collection[1]).getroot()
 
 root_all = root_1.append(root_2)
 #print(ET.dump(root_1))

 #print(dir(root))








if __name__ == '__main__':
    main()
