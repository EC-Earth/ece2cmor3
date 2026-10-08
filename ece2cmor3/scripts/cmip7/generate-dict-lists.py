#!/usr/bin/env python3

grid_nemo = [             \
             'T_2D'     , \
             'U_2D'     , \
             'V_2D'     , \
             'T_3D'     , \
             'U_3D'     , \
             'V_3D'     , \
             'W_3D'     , \
             'T_vsum'   , \
             'T_iax_20C', \
             'time'     , \
             'basin'    , \
             'other'      \
            ]

# To be adjusted:
grid_oifs = [             \
             'T_2D'     , \
             'U_2D'     , \
             'V_2D'     , \
             'T_3D'     , \
             'U_3D'     , \
             'V_3D'     , \
             'W_3D'     , \
             'T_vsum'   , \
             'T_iax_20C', \
             'time'     , \
             'basin'    , \
             'other'      \
            ]

frequency = [       \
             'fx' , \
             '1hr', \
             '3hr', \
             '6hr', \
             'day', \
             'mon', \
             'yr'   \
            ]

region    = [       \
             'glb', \
             'nh' , \
             'sh' , \
             's30'  \
            ]

def map_comment(region):
    if   region == 'glb':
     comment = 'Global'
    elif region == 'nh':
     comment = 'Northern hemisphere'
    elif region == 'sh':
     comment = 'Southern hemisphere'
    elif region == 's30':
     comment = '30S-90S'
    else:
     comment = ''
    return comment


def write_list_module(file_name, grid, head_file):
    dict_list_file = open(file_name, 'w')
    dict_list_file.write('{}\n'.format(head_file.strip()))
    for ii in grid:
     dict_list_file.write(' {:12}: {{\n'.format("'" + ii + "'"))
     for jj in frequency:
      dict_list_file.write('                 {:6}: {{\n'.format("'" + jj + "'"))
      for kk in region:
       if kk == region[-1]:
        dict_list_file.write('                           {:5} : []  # {}\n'.format("'" + kk + "'", map_comment(kk)))  # Closing
       else:
        dict_list_file.write('                           {:5} : [], # {}\n'.format("'" + kk + "'", map_comment(kk)))
      if jj == frequency[-1]:
       dict_list_file.write('                         }\n')                                                           # Closing
      else:
       dict_list_file.write('                         },\n')
     if ii == grid[-1]:
      dict_list_file.write('               }\n')                                                                      # Closing
     else:
      dict_list_file.write('               },\n')
    dict_list_file.write('}\n')
    dict_list_file.close()

head_nemo_file = \
'''
#!/usr/bin/env python3

nemo_dict = {
 # The nested dictionary of lists for NEMO with string indices for:
 #  grid_ref (or dimensional shape cases)
 #  frequency
 #  region
'''

head_oifs_file = head_nemo_file.replace('NEMO', 'OIFS').replace('nemo', 'oifs')

write_list_module('list_dict_nemo.py', grid_nemo, head_nemo_file)
write_list_module('list_dict_oifs.py', grid_oifs, head_oifs_file)
