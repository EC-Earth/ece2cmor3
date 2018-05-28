#!/usr/bin/env python
# Thomas Reerink

# Call this script by:
#  ./create-basic-ec-earth-cmip6-nemo-namelist.py
#  ./create-basic-ec-earth-cmip6-nemo-namelist.py; diff -b basic_cmip6_file_def_nemo-opa.xml bup-basic_cmip6_file_def_nemo-opa.xml;

# First, this script reads the shaconemo xml ping files (the files which relate NEMO code variable
# names with CMOR names. NEMO code names which are labeled by 'dummy_' have not been identified by
# the Shaconemo comunity.
#
# Second, this script reads the four NEMO xml field_def files (the files which contain the basic info
# about the fields required by XIOS. These field_def files can either be taken from the shaconemo
# repository or from the EC-Earth repository. The four field_def files contain nearly 1200 variables
# with an id (15 id's occur twice) and about 100 variables whithout an id but with a field_ref (most
# of the latter one have an name attribute, but not all of them).
#
# Third, the NEMO only excel xlsx CMIP6 data request file is read. This file has been created
# elsewhere by checking the non-dummy NEMO shaconemo ping file cmor variable list against the
# full CMIP6 data request for all CMIP6 MIPs in which EC-Earth participates, i.e. for tier 3
# and priority 3: about 320 unique cmor-table - cmor-variable-name combinations.
#
# Fourth, a few lists are created or or/and modified, some renaming or for instance selecting the
# output frequency per field from the cmor table label.
#
# Five, the basic ec-earth cmip6 nemo XIOS input file (the namelist or the file_def file) is written
# by combining all the available data. In this file for each variable the enable attribute is set to
# false, this allows another smaller program in ece2cmor3 to set those variables on true which are
# asked for in the various data requests of each individual MIP experiment. TO DO: make selections
# for sets of variables to be outputted in one file based on: output frequency, grid and model
# component.

import xml.etree.ElementTree as xmltree
import os.path                                                # for checking file existence with: os.path.isfile
import numpy as np                                            # for the use of e.g. np.multiply
from os.path import expanduser

ping_file_directory            = expanduser("~")+"/cmorize/shaconemo/ORCA1_LIM3_PISCES/EXP00/"
field_def_file_directory       = expanduser("~")+"/cmorize/shaconemo/ORCA1_LIM3_PISCES/EXP00/"
nemo_only_dr_nodummy_file_xlsx = expanduser("~")+"/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/nemo-only-list-cmpi6-requested-variables.xlsx"
nemo_only_dr_nodummy_file_txt  = expanduser("~")+"/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/bup-nemo-only-list-cmpi6-requested-variables.txt"


message_occurence_identical_id = True
message_occurence_identical_id = False

include_root_field_group_attributes = True
#include_root_field_group_attributes = False

exclude_dummy_fields = True
#exclude_dummy_fields = False

include_grid_ref_from_field_def_files = True
#include_grid_ref_from_field_def_files = False

################################################################################
###################################    1     ###################################
################################################################################

# READING THE PING FILES:

treeOcean     = xmltree.parse(ping_file_directory + "ping_ocean.xml")
treeSeaIce    = xmltree.parse(ping_file_directory + "ping_seaIce.xml")
treeOcnBgChem = xmltree.parse(ping_file_directory + "ping_ocnBgChem.xml")

rootOcean     = treeOcean.getroot()            # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
rootSeaIce    = treeSeaIce.getroot()           # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
rootOcnBgChem = treeOcnBgChem.getroot()        # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

field_elements_Ocean     = rootOcean    [0][:]
field_elements_SeaIce    = rootSeaIce   [0][:]
field_elements_OcnBgChem = rootOcnBgChem[0][:]

#field_elements_Ocean     = treeOcean.getroot()    [0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
#field_elements_SeaIce    = treeSeaIce.getroot()   [0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
#field_elements_OcnBgChem = treeOcnBgChem.getroot()[0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

#Exclude the dummy_ variables from the ping list and removes the CMIP6_ prefix.
pinglistOcean_id        = []
pinglistOcean_field_ref = []
pinglistOcean_text      = []
pinglistOcean_expr      = []
for child in field_elements_Ocean:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcean_id.append(child.attrib["id"][6:])
  pinglistOcean_field_ref.append(child.attrib["field_ref"])
  pinglistOcean_text.append(child.text)
 #pinglistOcean_expr.append(child.attrib["expr"])             # Not present in each element

pinglistSeaIce_id        = []
pinglistSeaIce_field_ref = []
pinglistSeaIce_text      = []
pinglistSeaIce_expr      = []
for child in field_elements_SeaIce:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistSeaIce_id.append(child.attrib["id"][6:])
  pinglistSeaIce_field_ref.append(child.attrib["field_ref"])
  pinglistSeaIce_text.append(child.text)
 #pinglistSeaIce_expr.append(child.attrib["expr"])            # Not present in each element

pinglistOcnBgChem_id        = []
pinglistOcnBgChem_field_ref = []
pinglistOcnBgChem_text      = []
pinglistOcnBgChem_expr      = []
for child in field_elements_OcnBgChem:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcnBgChem_id.append(child.attrib["id"][6:])
  pinglistOcnBgChem_field_ref.append(child.attrib["field_ref"])
  pinglistOcnBgChem_text.append(child.text)
 #pinglistOcnBgChem_expr.append(child.attrib["expr"])         # Not present in each element

total_pinglist_id        = pinglistOcean_id        + pinglistSeaIce_id        + pinglistOcnBgChem_id
total_pinglist_field_ref = pinglistOcean_field_ref + pinglistSeaIce_field_ref + pinglistOcnBgChem_field_ref
total_pinglist_text      = pinglistOcean_text      + pinglistSeaIce_text      + pinglistOcnBgChem_text
#total_pinglist_expr      = pinglistOcean_expr      + pinglistSeaIce_expr      + pinglistOcnBgChem_expr

if exclude_dummy_fields:
 print '\n There are ', len(total_pinglist_id), 'non-dummy variables taken from the shaconemo ping files.\n'
else:
 print '\n There are ', len(total_pinglist_id), 'variables taken from the shaconemo ping files.\n'

#print pinglistOcean_id
#print pinglistOcean_field_ref
#print pinglistOcean_text

#print rootOcean    [0][:]
#print field_elements_Ocean

#print rootOcean    [0].attrib["test"]          # Get an attribute of the parent element
#print rootOcean    [0][0].attrib["field_ref"]
#print rootOcean    [0][1].attrib["id"]
#print rootOcean    [0][:].attrib["id"]         # does not work, needs an explicit for loop

field_example = "tomint"  # Specify a cmor field name
field_example = "cfc11"  # Specify a cmor field name
index_in_ping_list = pinglistOcean_id.index(field_example)
#print index_in_ping_list, pinglistOcean_id[index_in_ping_list], pinglistOcean_field_ref[index_in_ping_list], pinglistOcean_text[index_in_ping_list]

# Create an XML file, see http://stackabuse.com/reading-and-writing-xml-files-in-python/
# mydata = xmltree.tostring(rootOcean)
# myfile = open("bla.xml", "w")
# myfile.write(mydata)


#history

#print rootOcean.attrib["id"], rootSeaIce.attrib["id"], rootOcnBgChem.attrib["id"]

#print field_elements_Ocean    [1].__dict__  # Example print of the 1st Ocean     field-element
#print field_elements_SeaIce   [1].__dict__  # Example print of the 1st SeaIce    field-element
#print field_elements_OcnBgChem[1].__dict__  # Example print of the 1st OcnBgChem field-element

#print field_elements_Ocean    [1].tag,field_elements_Ocean    [1].attrib["id"],field_elements_Ocean    [1].attrib["field_ref"],field_elements_Ocean    [1].text  # Example print of the tag and some specified attributes of the 1st Ocean     field-element
#print field_elements_SeaIce   [1].tag,field_elements_SeaIce   [1].attrib["id"],field_elements_SeaIce   [1].attrib["field_ref"],field_elements_SeaIce   [1].text  # Example print of the tag and some specified attributes of the 1st SeaIce    field-element
#print field_elements_OcnBgChem[1].tag,field_elements_OcnBgChem[1].attrib["id"],field_elements_OcnBgChem[1].attrib["field_ref"],field_elements_OcnBgChem[1].text  # Example print of the tag and some specified attributes of the 1st OcnBgChem field-element

#for field_elements in [field_elements_Ocean, field_elements_SeaIce, field_elements_OcnBgChem]:
#    for child in field_elements:
#        print child.attrib["id"], child.attrib["field_ref"], child.text

#print rootOcean[0][0].attrib["field_ref"]
#print rootOcean[0][0].text
#print rootOcean[0][1].attrib["expr"]
#print rootOcean[0][1].text


################################################################################
###################################    2     ###################################
################################################################################

# READING THE FIELD_DEF FILES:

def create_element_lists(file_name, attribute_1, attribute_2):
    tree = xmltree.parse(file_name)
    field_elements_attribute_1 = []    # The basic list in this routine containing the id attribute values
    field_elements_attribute_2 = []    # A corresponding list containing the grid_def attribute values
    fields_without_id_name      = []   # This seperate list is created for fields which don't have an id (most of them have a name attribute, but some only have a field_ref attribute)
    fields_without_id_field_ref = []   # A corresponding list with the field_ref attribute values is created. The other list contains the name attribute values if available, otherwise the name is assumed to be identical to the field_ref value.
    for group in range(0, len(tree.getroot())):
       #print ' Group ', group, 'of', len(tree.getroot()) - 1, 'in file:', file_name
        elements = tree.getroot()[group][:]                                             # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
        for child in elements:
         if attribute_1 in child.attrib:
          field_elements_attribute_1.append(child.attrib[attribute_1])
         #print ' ', attribute_1, ' = ', child.attrib[attribute_1]
          if attribute_2 in child.attrib:
           field_elements_attribute_2.append('grid_ref="'+child.attrib[attribute_2]+'"')
          #print ' ', attribute_2, ' = ', child.attrib[attribute_2]
          else:
           if attribute_2 in tree.getroot()[group].attrib:
            # In case the attribute is not present in th element definition, it is taken from its parent element:
            field_elements_attribute_2.append('GRID_REF="'+tree.getroot()[group].attrib[attribute_2]+'"');
           #print ' WARNING: No ', attribute_2, ' attribute for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', child.attrib
           else:
           #print ' WARNING: No ', attribute_2, ' attribute for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', tree.getroot()[group].attrib
            if 'do include domain ref' == 'do include domain ref':
            #print 'do include domain ref'
             if "domain_ref" in tree.getroot()[group].attrib:
              field_elements_attribute_2.append('domain_ref="'+tree.getroot()[group].attrib["domain_ref"]+'"')
             else:
              print ' ERROR: No ', 'domain_ref', ' attribute either for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', tree.getroot()[group].attrib
              field_elements_attribute_2.append(None)
            else:
             field_elements_attribute_2.append(None)
         else:
          # If the element has no id it should have a field_ref attribute, so checking for that:
          if "field_ref" in child.attrib:
           if "name" in child.attrib:
            fields_without_id_name.append(child.attrib["name"])
            fields_without_id_field_ref.append(child.attrib["field_ref"])
           #print ' This variable {:15} has no id but it has a field_ref = {}'.format(child.attrib["name"], child.attrib["field_ref"])
           else:
            fields_without_id_name.append(child.attrib["field_ref"])      # ASSUMPTION about XIOS logic: in case no id and no name attribute are defined inside an element, it is assumed that the value of the field_ref attribute is taken as the value of the name attribute
            fields_without_id_field_ref.append(child.attrib["field_ref"])
           #print ' This variable {:15} has no id and no name, but it has a field_ref = {:15} Its full attribute list: {}'.format('', child.attrib["field_ref"], child.attrib)
          else:
           print ' ERROR: No ', attribute_1, 'and no field_ref attribute either for this variable. This element has the attributes: ', child.attrib

   #for item in range(0,len(fields_without_id_name)):
   # print ' This variable {:15} has no id but it has a field_ref = {}'.format(fields_without_id_name[item], fields_without_id_field_ref[item])
   #print ' The length of the list with fields without an id is: ', len(fields_without_id_name)
    return field_elements_attribute_1, field_elements_attribute_2, fields_without_id_name, fields_without_id_field_ref


field_def_nemo_opa_id     , field_def_nemo_opa_grid_ref     , no_id_field_def_nemo_opa_name     , no_id_field_def_nemo_opa_field_ref      = create_element_lists(ping_file_directory + "field_def_nemo-opa.xml"     , "id", "grid_ref")
field_def_nemo_lim_id     , field_def_nemo_lim_grid_ref     , no_id_field_def_nemo_lim_name     , no_id_field_def_nemo_lim_field_ref      = create_element_lists(ping_file_directory + "field_def_nemo-lim.xml"     , "id", "grid_ref")
field_def_nemo_pisces_id  , field_def_nemo_pisces_grid_ref  , no_id_field_def_nemo_pisces_name  , no_id_field_def_nemo_pisces_field_ref   = create_element_lists(ping_file_directory + "field_def_nemo-pisces.xml"  , "id", "grid_ref")
field_def_nemo_inerttrc_id, field_def_nemo_inerttrc_grid_ref, no_id_field_def_nemo_inerttrc_name, no_id_field_def_nemo_inerttrc_field_ref = create_element_lists(ping_file_directory + "field_def_nemo-inerttrc.xml", "id", "grid_ref")


total_field_def_nemo_id              = field_def_nemo_opa_id              + field_def_nemo_lim_id              + field_def_nemo_pisces_id              + field_def_nemo_inerttrc_id
total_field_def_nemo_grid_ref        = field_def_nemo_opa_grid_ref        + field_def_nemo_lim_grid_ref        + field_def_nemo_pisces_grid_ref        + field_def_nemo_inerttrc_grid_ref
total_no_id_field_def_nemo_name      = no_id_field_def_nemo_opa_name      + no_id_field_def_nemo_lim_name      + no_id_field_def_nemo_pisces_name      + no_id_field_def_nemo_inerttrc_name
total_no_id_field_def_nemo_field_ref = no_id_field_def_nemo_opa_field_ref + no_id_field_def_nemo_lim_field_ref + no_id_field_def_nemo_pisces_field_ref + no_id_field_def_nemo_inerttrc_field_ref

#for item in range(0,len(total_no_id_field_def_nemo_name)):
# print ' This variable {:15} has no id but it has a field_ref = {}'.format(total_no_id_field_def_nemo_name[item], total_field_def_nemo_grid_ref[item])
print ' The length of the list with fields without an id is: ', len(total_no_id_field_def_nemo_name)

print '\n In total there are', len(total_field_def_nemo_id), 'fields defined in the field_def files, with', len(total_field_def_nemo_id) - len(list(set(total_field_def_nemo_id))), 'double occurence.\n'

#print field_def_nemo_opa_id

#print list(set(total_field_def_nemo_id))
#print list(set(total_field_def_nemo_grid_ref))
#print total_field_def_nemo_id
#print total_field_def_nemo_grid_ref


################################################################################
def check_all_list_elements_are_identical(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

def check_which_list_elements_are_identical(list_of_attribute_1, list_of_attribute_2):
    for child in list_of_attribute_1:
     indices_identical_ids = get_indexes(child, list_of_attribute_1)
    #print len(indices_identical_ids), indices_identical_ids
     id_list       = []
     grid_ref_list = []
     for identical_child in range(0,len(indices_identical_ids)):
      id_list      .append(list_of_attribute_1[indices_identical_ids[identical_child]])
      grid_ref_list.append(list_of_attribute_2[indices_identical_ids[identical_child]])
     #print indices_identical_ids[identical_child], list_of_attribute_1[indices_identical_ids[identical_child]], list_of_attribute_2[indices_identical_ids[identical_child]]
     if not check_all_list_elements_are_identical(id_list)      : print ' WARNING: Different ids in sublist [should never occur] at positions:', indices_identical_ids, id_list
     if not check_all_list_elements_are_identical(grid_ref_list): print ' WARNING: The variable {:22} has different grid definitions, at positions: {:20} with grid: {}'.format(id_list[0] , indices_identical_ids, grid_ref_list)
     if message_occurence_identical_id and len(indices_identical_ids) > 1: print ' The variable {:22} occurs more than once, at positions: {:20} with grid: {}'.format(id_list[0] , indices_identical_ids, grid_ref_list)

#  output_nemo_opa_xml_file.write('{:40} {:25} {:40} {:20} {:20} {:15} {:17} {:50} {:15} {:22} {:60} {:4} {:60} {:10} {}'.format('     <field id="CMIP6_'+dr_varname[i]+'" ', 'name="'+dr_varname[i]+'"', '  field_ref="'+total_pinglist_field_ref[index_in_ping_list]+'"', '  grid_ref="'+grid_ref+'"',  dr_output_frequency[i], '  enable="False"', '  field_nr="'+str(number_of_field_element)+'"', '  grid_shape="'+dr_vardim[i]+'"', 'table="'+dr_table[i]+'"', ' component="'+dr_ping_component[i]+'"', root_field_group_attributes, ' > ', total_pinglist_text[index_in_ping_list], ' </field>', '\n'))

#check_which_list_elements_are_identical(field_def_nemo_opa_id      , field_def_nemo_opa_grid_ref      )
#check_which_list_elements_are_identical(field_def_nemo_lim_id      , field_def_nemo_lim_grid_ref      )
#check_which_list_elements_are_identical(field_def_nemo_pisces_id   , field_def_nemo_pisces_grid_ref   )
#check_which_list_elements_are_identical(field_def_nemo_inerttrc_id , field_def_nemo_inerttrc_grid_ref )
check_which_list_elements_are_identical(total_field_def_nemo_id, total_field_def_nemo_grid_ref)

#x = [ 'w', 'e', 's', 's', 's', 'z','z', 's']
#print [i for i, n in enumerate(x) if n == 's']
################################################################################

#print tree_field_def_nemo_opa.getroot().attrib["level"]                         # example of getting an attribute value of the root  element: the field_definition element
#print tree_field_def_nemo_opa.getroot()[0].attrib["id"]                         # example of getting an attribute value of its child element: the field_group      element
#print tree_field_def_nemo_opa.getroot()[0].attrib["grid_ref"]                   # example of getting an attribute value of its child element: the field_group      element
#print field_def_nemo_opa[0].attrib["id"],                                       # example of getting an attribute value of its child element: the field            element
#print field_def_nemo_opa[0].attrib["grid_ref"]                                  # example of getting an attribute value of its child element: the field            element

################################################################################
###################################    3     ###################################
################################################################################

# READING THE NEMO DATA REQUEST FILES:


# This function can be used to read any excel file which has been produced by the checkvars.py script, 
# in other words it can read the pre basic ignored, the pre basic identified missing, basic ignored, 
# basic identified missing, available, ignored, identified-missing, and missing files.
def load_checkvars_excel(excel_file):
    import xlrd
    table_colname       = "Table"                                        # CMOR table name
    var_colname         = "variable"                                     # CMOR variable name
    prio_colname        = "prio"                                         # priority of variable
    dimension_colname   = "Dimension format of variable"                 # 
    longname_colname    = "variable long name"                           # 
    link_colname        = "link"                                         # 
    comment_colname     = "comment"                                      # for the purpose here: this is the model component
    author_colname      = "comment author"                               # 
    description_colname = "extensive variable description"               # 
    miplist_colname     = "list of MIPs which request this variable"     # 

    book = xlrd.open_workbook(excel_file)
    for sheetname in book.sheet_names():
        if sheetname.lower() in ["notes"]:
            continue
        sheet = book.sheet_by_name(sheetname)
        header = sheet.row_values(0)
        coldict = {}
        for colname in [table_colname, var_colname, prio_colname, dimension_colname, comment_colname, miplist_colname]:
            if colname not in header:
              print " Could not find the column: ", colname, " in the sheet", sheet, "\n in the file", excel_file, "\n"
              quit()
            coldict[colname] = header.index(colname)
        nr_of_header_lines = 2
        tablenames   = [c.value for c in sheet.col_slice(colx=coldict[table_colname    ], start_rowx = nr_of_header_lines)]
        varnames     = [c.value for c in sheet.col_slice(colx=coldict[var_colname      ], start_rowx = nr_of_header_lines)]
        varpriority  = [c.value for c in sheet.col_slice(colx=coldict[prio_colname     ], start_rowx = nr_of_header_lines)]
        vardimension = [c.value for c in sheet.col_slice(colx=coldict[dimension_colname], start_rowx = nr_of_header_lines)]
        comments     = [c.value for c in sheet.col_slice(colx=coldict[comment_colname  ], start_rowx = nr_of_header_lines)]
        miplist      = [c.value for c in sheet.col_slice(colx=coldict[miplist_colname  ], start_rowx = nr_of_header_lines)]
    return tablenames, varnames, varpriority, vardimension, comments, miplist

# Read the excel file with the NEMO data request:
dr_table, dr_varname, dr_varprio, dr_vardim, dr_ping_component, dr_miplist = load_checkvars_excel(nemo_only_dr_nodummy_file_xlsx)

#print dr_miplist[0]

################################################################################
###################################    4     ###################################
################################################################################


################################################################################
# Convert the model component labeling in the ping file naming to the model component name in NEMO:
for element_counter in range(0,len(dr_ping_component)):
 if dr_ping_component[element_counter] == "ocean"    : dr_ping_component[element_counter] = "opa"
 if dr_ping_component[element_counter] == "seaIce"   : dr_ping_component[element_counter] = "lim"
 if dr_ping_component[element_counter] == "ocnBgChem": dr_ping_component[element_counter] = "pisces"
################################################################################


################################################################################
# Create the output_freq attribute from the table name:
table_list_of_dr = list(set(dr_table))
for table in range(0,len(table_list_of_dr)):
 if not table_list_of_dr[table] in set(["", "SImon", "Omon", "SIday", "Oyr", "Oday", "Oclim", "Ofx", "Odec"]): print "\n No rule defined for the encountered table: ", table_list_of_dr[table], "\n This probably needs an additon to the code of create-basic-ec-earth-cmip6-nemo-namelist.py.\n"

# Creating a list with the output_freq attribute and its value if a relevant value is known, otherwise omit attribute definiton:
dr_output_frequency = dr_table[:]  # Take care here: a slice copy is needed.
for table in range(0,len(dr_table)):
 if dr_table[table] == "SImon" or dr_table[table] == "Omon" : dr_output_frequency[table] = 'output_freq="mo"'    # mo stands in XIOS for monthly output
 if dr_table[table] == "SIday" or dr_table[table] == "Oday" : dr_output_frequency[table] = 'output_freq="d"'     # d  stands in XIOS for dayly   output
 if                               dr_table[table] == "Oyr"  : dr_output_frequency[table] = 'output_freq="y"'     # y  stands in XIOS for yearly  output
 if                               dr_table[table] == "Oclim": dr_output_frequency[table] = ""                    # Does not match XIOS calendar units
 if                               dr_table[table] == "Ofx"  : dr_output_frequency[table] = ""                    # Does not match XIOS calendar units
 if                               dr_table[table] == "Odec" : dr_output_frequency[table] = ""                    # Does not match XIOS calendar units
################################################################################


################################################################################
# Instead of pulling these attribute values from the root element, the field_group element, in the field_def files, we just define them here:
if include_root_field_group_attributes:
#root_field_group_attributes ='level="1" prec="4" operation="average" enabled=".TRUE." default_value="1.e20"'
 root_field_group_attributes ='level="1" prec="4" operation="average" default_value="1.e20"'
else:
 root_field_group_attributes =''
################################################################################



################################################################################
###################################    5     ###################################
################################################################################

# WRITING THE NEMO FILE_DEF FILES FOR CMIP6 FOR EC_EARTH:

output_nemo_opa_xml_file = open('basic_cmip6_file_def_nemo-opa.xml','w')
output_nemo_opa_xml_file.write('<?xml version="1.0"?> \n\n  <file_defenition type="one_file"  name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" min_digits="4">  \n')
output_nemo_opa_xml_file.write('\n\n   <file_group>\n')
output_nemo_opa_xml_file.write('\n\n    <file>\n\n')

i = 0
number_of_field_element = 0
nr_of_missing_fields_in_field_def = 0
nr_of_available_fields_in_field_def = 0

# Looping through the NEMO data request (which is currently based on the non-dummy ping file variables). The dr_varname list contains cmor variable names.
for i in range(0, len(dr_varname)):
#print dr_varname[i], dr_varname.index(dr_varname[i]), i, dr_table[i], dr_varname[i], dr_varprio[i], dr_vardim[i], dr_ping_component[i], dr_miplist[i]
 if not dr_varname[i] == "":
  number_of_field_element = number_of_field_element + 1
  index_in_ping_list = total_pinglist_id.index(dr_varname[i])
 #print ' {:20} {:20} {:20} '.format(dr_varname[i], total_pinglist_id[index_in_ping_list])
 #if not dr_varname[i] == total_pinglist_id[index_in_ping_list]: print ' WARNING: Different names [should not occur]:', dr_varname[i], total_pinglist_id[index_in_ping_list]

  # Creating a list with the grid_ref attribute and its value as abstracted from the field_def files, otherwise omit attribute definiton:
  if include_grid_ref_from_field_def_files:
   # Adding the grid_def attribute with value (or alternatively the domain_ref attribute with value):
   if not total_pinglist_field_ref[index_in_ping_list] in total_field_def_nemo_id:
    nr_of_missing_fields_in_field_def = nr_of_missing_fields_in_field_def + 1
    print 'missing:   ', nr_of_missing_fields_in_field_def, total_pinglist_field_ref[index_in_ping_list]
   else:
    nr_of_available_fields_in_field_def = nr_of_available_fields_in_field_def + 1
   #print 'available: ', nr_of_available_fields_in_field_def, total_pinglist_field_ref[index_in_ping_list]
    index_in_field_def_list = total_field_def_nemo_id.index(total_pinglist_field_ref[index_in_ping_list])
    grid_ref = total_field_def_nemo_grid_ref[index_in_field_def_list]
   #print index_in_field_def_list, total_field_def_nemo_grid_ref[index_in_field_def_list]
  else:
  #grid_ref = 'grid_ref="??"'
   grid_ref = ''

 #print i, number_of_field_element, " cmor table = ", dr_table[i], " cmor varname = ", dr_varname[i], " model component = ", dr_ping_component[i], "  nemo code name = ", total_pinglist_field_ref[index_in_ping_list], "  expression = ", total_pinglist_text[index_in_ping_list], " ping idex = ", index_in_ping_list
 #print index_in_ping_list, pinglistOcean_id[index_in_ping_list], pinglistOcean_field_ref[index_in_ping_list], pinglistOcean_text[index_in_ping_list]
 #                                                                                                                                                                       40,                         25,                                                               40,       32,                      20,                 15,                                              17,                                50,                        15,                                      22,                        [60],     4,                                      60,          10,   {}))
# output_nemo_opa_xml_file.write('{:40} {:25} {:40} {:32} {:20} {:15} {:17} {:50} {:15} {:22}       {:4} {:60} {:10} {}'.format('     <field id="CMIP6_'+dr_varname[i]+'" ', 'name="'+dr_varname[i]+'"', '  field_ref="'+total_pinglist_field_ref[index_in_ping_list]+'"', grid_ref,  dr_output_frequency[i], '  enable="False"', '  field_nr="'+str(number_of_field_element)+'"', '  grid_shape="'+dr_vardim[i]+'"', 'table="'+dr_table[i]+'"', ' component="'+dr_ping_component[i]+'"',                              ' > ', total_pinglist_text[index_in_ping_list], ' </field>', '\n'))
  output_nemo_opa_xml_file.write('{:40} {:25} {:40} {:32} {:20} {:15} {:17} {:50} {:15} {:22} {:60} {:4} {:60} {:10} {}'.format('     <field id="CMIP6_'+dr_varname[i]+'" ', 'name="'+dr_varname[i]+'"', '  field_ref="'+total_pinglist_field_ref[index_in_ping_list]+'"', grid_ref,  dr_output_frequency[i], '  enable="False"', '  field_nr="'+str(number_of_field_element)+'"', '  grid_shape="'+dr_vardim[i]+'"', 'table="'+dr_table[i]+'"', ' component="'+dr_ping_component[i]+'"', root_field_group_attributes, ' > ', total_pinglist_text[index_in_ping_list], ' </field>', '\n'))
#else:
# print i, " Empty line" # Filter the empty lines in the xlsx between the table blocks.


output_nemo_opa_xml_file.write('\n\n    </file>\n')
output_nemo_opa_xml_file.write('\n\n   </file_group>\n')
output_nemo_opa_xml_file.write('\n\n  </file_defenition>\n')




################################################################################
###################################   End    ###################################
################################################################################





# TO DO:
#  Split file_def file in the 3 context file_def files for opa, lim, pisces
#  Distinguish per output frequency by taking a different file group element and set the output_freq attribute.
#  Distinguish per staggered grid by taking a different file element and set the grid_ref attribute.
#  Create a nemo only for all NEMO ping variables including ping dummy vars. Are there variables not in ping but present in data request?
#  DONE: Is it possible to read the field_def files and pull the grid_ref for each field element from the parent element?
#  Add prio, add miplist, long name, description, link, comment
#  Check: Does the most general file contain all tier, prio = 3 and include all ping dummy variables?
#  Does the added field_def_nemo-inerttrc.xml for pisces need any additional action?

# Add script which reads ping file xml files and write the nemo only pre basic xmls file.



#   ofile.write('{:10} {:20} {:5} {:40} {:95} {:98} {:20} {} {}'.format('table', 'variable', 'prio', 'dimensions', 'long_name', 'list of MIPs which request this variable', 'comment_author', 'comment', '\n'))
#  #ofile.write('{:10} {:20} {:10} {:40} {:5} {:95} {:98} {}'.format('table', 'variable', 'component', 'dimensions', 'prio', 'long_name', 'list of MIPs which request this variable', '\n'))
#           ofile.write('{:10} {:20} {:5} {:40} {:95} {:98} {:20} {} {}'.format(tgtvar.table, tgtvar.variable, tgtvar.priority, getattr(tgtvar,"dimensions","unknown"), getattr(tgtvar,"long_name","unknown"), tgtvar.mip_list, getattr(tgtvar,"comment_author",""), getattr(tgtvar,"ecearth_comment",""), '\n'))
#          #ofile.write('{:10} {:20} {:10} {:40} {:5} {:95} {:98} {}'.format(tgtvar.table, tgtvar.variable, getattr(tgtvar,"ecearth_comment",""), getattr(tgtvar,"dimensions","unknown"), tgtvar.priority, getattr(tgtvar,"long_name","unknown"), tgtvar.mip_list, '\n'))
 


 
#def write_xios_xml_namelist(targets,opath):
#    ofile = open(opath,'w')
#    ofile.write('<?xml version="1.0"?> \n\n  <file_defenition type=""  name="">  \n\n')
#    for k,vlist in tgtgroups.iteritems():
#        ofile.write('{}'.format('\n'))
#        for tgtvar in vlist:
#            ofile.write('{:15} {:25} {:50} {:15} {:50} {}'.format('   <field id="" ', 'name="'+tgtvar.variable+'"', '  grid_ref="'+getattr(tgtvar,"dimensions","unknown")+'"', 'table="'+tgtvar.table+'"', ' component="'+getattr(tgtvar,"ecearth_comment","")+'" />', '\n'))
#           #ofile.write('{:19} {:20} {:13} {:40} {:20} {:50} {:5} {}'.format('<field id="" ', 'name="'+tgtvar.variable+'"', '  grid_ref="', getattr(tgtvar,"dimensions","unknown"), '" component="', getattr(tgtvar,"ecearth_comment",""), '" />', '\n'))
#           #ofile.write('{:10} {:20} {:5} {:40} {:95} {:60} {:20} {} {}'.format(tgtvar.table, tgtvar.variable, tgtvar.priority, getattr(tgtvar,"dimensions","unknown"), getattr(tgtvar,"long_name","unknown"), tgtvar.mip_list, getattr(tgtvar,"comment_author",""), getattr(tgtvar,"ecearth_comment",""), '\n'))
#    ofile.write('\n\n  </file_defenition>\n')
#    ofile.close()

#write_xios_xml_namelist(identifiedmissingtargets,args.output + ".nemo-xios-namelist.xml")




# # Create the xml file structure with xmltree:
# file_definition_element = xmltree.Element('file_definition')                   # Defines the root element
# file_element            = xmltree.SubElement(file_definition_element, 'file')
# field_element_1         = xmltree.SubElement(file_element, 'field')
# field_element_2         = xmltree.SubElement(file_element, 'field')
# field_element_3         = xmltree.SubElement(file_element, 'field')
# field_element_1.set('name','field 1')
# field_element_2.set('name','field 2')
# field_element_3.set('name','field 3')
# field_element_1.set('id','id field 1')
# field_element_2.set('id','id field 2')
# field_element_3.set('id','id field 3')

# # Write the xml file with xmltree:
# general_nemo_file_def_file = open("general_xios_file_def.xml", "w")
# general_nemo_file_def_file.write(xmltree.tostring(file_definition_element))

##tree = xmltree.parse('general_xios_file_def.xml')
##tree.write('newgeneral_xios_file_def.xml')

## create the file structure
#data = ET.Element('data')
#items = ET.SubElement(data, 'items')
#item1 = ET.SubElement(items, 'item')
#item2 = ET.SubElement(items, 'item')
#item1.set('name','item1')
#item2.set('name','item2')
#item1.text = 'item1abc'
#item2.text = 'item2abc'



# Below a block with an alternative way of reading the data request, i.e. instead of the xlsx a ascii file is read:

# # Checking if the file exist:
# if os.path.isfile(nemo_only_dr_nodummy_file_txt) == False: print(' The  ', nemo_only_dr_nodummy_file_txt, '  does not exist.'); sys.exit(' stop')

# #data_entire_file    = np.loadtxt(nemo_only_dr_nodummy_file_txt, skiprows=2)
# # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.genfromtxt.html#numpy.genfromtxt
# data_entire_file    = np.genfromtxt(nemo_only_dr_nodummy_file_txt, dtype=None, comments='#', delimiter=None, skip_header=2, skip_footer=0, converters=None, missing_values=None, filling_values=None, usecols=None, names=None, excludelist=None, deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', unpack=None, usemask=False, loose=True, invalid_raise=True, max_rows=None)
# number_of_data_rows    = data_entire_file.shape[0]
# number_of_data_columns = data_entire_file.shape[1]
# #print data_entire_file[5][1] # print the element at the 6th line, 2nd column
# ##print data_entire_file[:][1] # This does not work as expected
# #print number_of_data_rows, number_of_data_columns
