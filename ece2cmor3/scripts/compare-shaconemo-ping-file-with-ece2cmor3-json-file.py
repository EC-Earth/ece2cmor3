#!/usr/bin/env python

# Call this script by:
#  python compare-shaconemo-ping-file-with-ece2cmor3-json-file.py

# This script reads the shaconemo xml ping file (the file which relates NEMO code variable
# names with CMOR names, code names which are labeled by 'dummy_' are not identified yet by
# the Shaconemo comunity) and the ece2cmor3 json file which lists all NEMO variables which 
# can be cmorized by ece2cmor3 yet. The script shows which variables are only in one of the
# files available.

import xml.etree.ElementTree as xmltree
import json
from os.path import expanduser

ping_file_directory = expanduser("~")+"/cmorize/shaconemo/ORCA1_LIM3_PISCES/EXP00/"

treeOcean     = xmltree.parse(ping_file_directory + "ping_ocean.xml")
treeSeaIce    = xmltree.parse(ping_file_directory + "ping_ocnBgChem.xml")
treeOcnBgChem = xmltree.parse(ping_file_directory + "ping_seaIce.xml")

rootOcean     = treeOcean.getroot()
rootSeaIce    = treeSeaIce.getroot()
rootOcnBgChem = treeOcnBgChem.getroot()

fdefOcean     = rootOcean    [0]
fdefSeaIce    = rootSeaIce   [0]
fdefOcnBgChem = rootOcnBgChem[0]

#print root.attrib["id"]

#print fdef[1].__dict__

#print fdef[1].tag,fdef[1].attrib["id"],fdef[1].attrib["field_ref"],fdef[1].text

#for child in fdef:
#    print child.attrib["id"],child.attrib["field_ref"],child.text

#pinglistOcean     = [child.attrib["id"][6:] for child in fdefOcean    ]
#pinglistSeaIce    = [child.attrib["id"][6:] for child in fdefSeaIce   ]
#pinglistOcnBgChem = [child.attrib["id"][6:] for child in fdefOcnBgChem]

pinglistOcean = []
for child in fdefOcean:
 if child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcean.append(child.attrib["id"][6:])

pinglistSeaIce = []
for child in fdefSeaIce:
 if child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistSeaIce.append(child.attrib["id"][6:])

pinglistOcnBgChem = []
for child in fdefOcnBgChem:
 if child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcnBgChem.append(child.attrib["id"][6:])


pinglist = pinglistOcean + pinglistSeaIce + pinglistOcnBgChem

f = open("../resources/nemopar.json").read()
data = json.loads(f)
#print data

targets = []
for d in data:
    targets.append(str(d["target"]))
#print targets
print '\n The ', len(set(targets) - set(pinglist)), ' variables which are in the ece2cmor3 json file but not in the ping file:\n ', set(targets) - set(pinglist)
print '\n The ', len(set(pinglist) - set(targets)), ' variables which are in the ping file but not in the ece2cmor3 json file:\n ', set(pinglist) - set(targets)
print '\n There are ', len(targets), ' variables in the ece2cmor3 nemopar.json file, and ', len(pinglist), 'non-dummy variables in the shaconemo ping file'
print '\n There are ', len(set(targets) & set(pinglist)), ' variables with the same name in both files\n'

#history
