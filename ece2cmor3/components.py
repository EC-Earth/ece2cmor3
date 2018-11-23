import os
import logging

# Logger instance
log = logging.getLogger(__name__)

table_file = "table_file"
realms = "realms"
script_flags = "option_keys"

# List of components, used to determine the script arguments and used by task loader.
# Add your NEWCOMPONENT to this dictionary if you want to extend ece2cmor3 to more models.
models = {"ifs": {realms: ["atmos", "atmosChem", "land", "landIce", "ocean", "seaIce"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "ifspar.json"),
                  script_flags: ("atm", 'a')},
          "nemo": {realms: ["ocean", "ocnBgchem", "seaIce"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "nemopar.json"),
                   script_flags: ("oce", 'o')},
          "lpjg": {realms: ["land", "atmos"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "lpjgpar.json"),
                   script_flags: ("lpj", 'l')},
          "tm5": {realms: ["aerosol", "atmosChem", "atmos"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "tm5par.json"),
                  script_flags: ("tm5", 't')}
          }


def get_script_options(name):
    flags = models[name].get(script_flags, ())
    if isinstance(flags, str):
        return flags, None
    if isinstance(flags, tuple) or isinstance(flags, list):
        if len(flags) == 0:
            return name, None
        if len(flags) == 1:
            return flags[0], None
        if len(flags[1]) != 1:
            log.error("Second script option %s for component %s should be single-character prefix option, ignoring "
                      "script option" % (flags[1], name))
            return flags[0], None
        return flags[0], flags[1]
    log.error("Script option %s for component %s is not iterable, ignoring input and using --%s"
              % (str(flags), name, name))
    return name, None


def load_parameter_table(component, filename):
    if component in models:
        models[component][table_file] = filename
