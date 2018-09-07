#!/usr/bin/env python
# Thomas Reerink
#
# Run example:
#  python mip-experiment-list.py
#
# Looping over all MIPs and within each MIP over all its MIP experiments.
# Printing the MIP experiment list with some additional info.
#

from dreqPy import dreq
dq = dreq.loadDreq()

mip_list_file= open( 'mip-experiment-list.txt', 'w' )

# Loop over the MIPs:
for mip in dq.coll['mip'].items:
  # Loop over the MIP experiments:
  for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
    ex = dq.inx.uid[u]
    mip_list_file.write( '{:20} {:20} {:30} {:3} {}'.format(mip.label, ex.mip, ex.label, ex.tier[0], ex.title) + '\n')
   #print '{:20} {:20} {:30} {:3} {}'.format(mip.label, ex.mip, ex.label, ex.tier[0], ex.title)

mip_list_file.close()
