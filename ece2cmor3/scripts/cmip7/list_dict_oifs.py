#!/usr/bin/env python3

oifs_dict = {
 # The nested dictionary of lists for OIFS with string indices for:
 #  grid_ref (or dimensional shape cases)
 #  frequency
 #  region
 'reduced_ml'    : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'reduced_plev19': {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'reduced_plev39': {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'reduced_pv'    : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'reduced_sfc'   : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'reduced_th'    : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'time'          : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   },
 'other'         : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : [], # 30S-90S
                              'grl' : []  # Greenland area
                            }
                   }
}
