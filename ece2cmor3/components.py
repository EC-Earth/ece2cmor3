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
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "tm5par.json")}
          }


def load_parameter_table(component, filename):
    if component in models:
        models[component][table_file] = filename
