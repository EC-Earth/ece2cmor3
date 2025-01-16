import os
import logging

# Logger instance
log = logging.getLogger(__name__)

table_file = "table_file"
realms = "realms"

# List of components, used to determine the script arguments and used by task loader.
# Add your NEWCOMPONENT to this dictionary if you want to extend ece2cmor3 to more models.
models = {"ifs": {realms: ["atmos", "atmosChem", "land", "landIce", "ocean", "seaIce"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "ifspar.json")},
          "nemo": {realms: ["ocean", "ocnBgchem", "seaIce"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "nemopar.json")},
          "lpjg": {realms: ["land", "atmos"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "lpjgpar.json")},
          "tm5": {realms: ["aerosol", "atmosChem", "atmos"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "tm5par.json")},
          "co2box": {realms: ["atmosChem"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "co2boxpar.json")}
          }

ece_configs = {'EC-EARTH-AOGCM'   : ["ifs", "nemo"                         ],
               'EC-EARTH-HR'      : ["ifs", "nemo"                         ],
               'EC-EARTH-LR'      : ["ifs", "nemo"                         ],
               'EC-EARTH-CC'      : ["ifs", "nemo", "tm5", "lpjg"          ],
               'EC-EARTH-ESM-1'   : ["ifs", "nemo",        "lpjg", "co2box"], # If a PISM component is added to ece2cmor3 it needs here to be added as well.
               'EC-EARTH-AerChem' : ["ifs", "nemo", "tm5"                  ],
               'EC-EARTH-Veg'     : ["ifs", "nemo",        "lpjg"          ],
               'EC-EARTH-Veg-LR'  : ["ifs", "nemo",        "lpjg"          ]}

def load_parameter_table(component, filename):
    if component in models:
        models[component][table_file] = filename
