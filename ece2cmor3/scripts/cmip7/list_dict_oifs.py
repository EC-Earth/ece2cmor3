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
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'reduced_plev19': {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'reduced_plev39': {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'reduced_pv'    : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'reduced_sfc'   : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'reduced_th'    : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'time'          : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   },
 'other'         : {
                    'fx'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '1hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '3hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    '6hr' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'day' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'mon' : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            },
                    'yr'  : {
                              'glb' : [], # Global
                              'nh'  : [], # Northern hemisphere
                              'sh'  : [], # Southern hemisphere
                              's30' : []  # 30S-90S
                            }
                   }
}
