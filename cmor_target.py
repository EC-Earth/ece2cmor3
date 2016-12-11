import os
import re
import json
import logging

# Log object.
log = logging.getLogger(__name__)


# Axes information read from tables.
axes = {}


# Class for cmor target objects, which represent output variables.
class cmor_target(object):

    def __init__(self,var_id__,tab_id__):
        self.variable = var_id__
        self.table = tab_id__
        self.dims = 2


# Derives the table id for the given file path
def get_table_id(filepath,prefix):
    fname = os.path.basename(filepath)
    regex = re.search("^" + prefix + "_.*.json$",fname)
    if(not regex):
        raise Exception("Unable to match file name",fname,"as cmor table json-file with prefix",prefix)
    return regex.group()[len(prefix) + 1:len(fname) - 5]


# Json file keys:
head_key = "header"
axis_key = "axis_entry"
var_key = "variable_entry"
freq_key = "frequency"
realm_key = "realm"
dims_key = "dimensions"
levs_key = "generic_levels"
cell_measures_key = "cell_measures"
cell_methods_key = "cell_methods"
valid_min_key = "valid_min"
valid_max_key = "valid_max"
cell_measure_axes = ["time","area","volume","latitude","longitude","depth"]


# Creates cmor-targets from the input json-file
def create_targets_for_file(filepath,prefix):
    tabid = get_table_id(filepath,prefix)
    s = open(filepath).read()
    result = []
    try:
        data = json.loads(s)
    except ValueError as err:
        log.warning("Input table %s has been ignored. Reason: %s" % (filepath,format(err)))
        return result
    freq = None
    realm = None
    header = get_lowercase(data,head_key,None)
    modlevs = None
    if(header):
        freq = get_lowercase(header,freq_key,None)
        realm = get_lowercase(header,realm_key,None)
        modlevs = get_lowercase(header,levs_key,None)
    axes_entries = get_lowercase(data,axis_key,{})
    if(modlevs):
        for modlev in modlevs.split():
            axes_entries[modlev] = {"requested":"all"}
    axes[tabid] = axes_entries
    var_entries = get_lowercase(data,var_key,{})
    for k,v in var_entries.iteritems():
        target = cmor_target(k,tabid)
        target.frequency = freq
        target.realm = realm
        for k2,v2 in v.iteritems():
            key = k2.lower()
            setattr(target,key,v2)
            if(key == dims_key.lower()):
                spacedims = list(set([s for s in v2.split() if not s.lower().startswith("time")]) - set(["basin"]))
                target.dims = len(spacedims)
                zdims = list(set(spacedims)-set(["latitude","longitude"]))
                if(any(zdims)):
                    setattr(target,"z_dims",zdims)
            if(key in [cell_measures_key.lower(),cell_methods_key.lower()]):
                cell_measure_str = v2.strip()
                if(cell_measure_str not in ["@OPT","--OPT","",None]):
                    cell_measures = cell_measure_str.split(':')
                    for i in range(1,len(cell_measures)):
                        prev_words = cell_measures[i-1].split()
                        if(len(prev_words) == 0):
                            log.error("Error parsing cell measures %s for variable %s in table %s" % (v2,k,tabid))
                            break
                        measure_dim = prev_words[-1].strip().lower()
                        if(measure_dim not in cell_measure_axes):
                            log.error("Error parsing cell measures %s for variable %s in table %s" % (v2,k,tabid))
                            break
                        key = measure_dim + "_operator"
                        value = cell_measures[i].strip().lower()
                        if(i < len(cell_measures) - 1):
                            value = ' '.join(value.split(' ')[:-1])
                        if(hasattr(target,key)):
                            getattr(target,key).append(value)
                        else:
                            setattr(target,key,[value])
	if(validate_target(target)): result.append(target)
    return result


# Utility function for lower-case dictionary searches
def get_lowercase(dictionary,key,default):
    if(not isinstance(key,basestring)): return dictionary.get(key,default)
    lowerkey = key.lower()
    for k,v in dictionary.iteritems():
        if(isinstance(k,basestring) and k.lower() == lowerkey): return v
    return default


# Creates cmor-targets from all json files in the given directory, with argument prefix.
def create_targets(path,prefix):
    if(os.path.isfile(path)):
        return create_targets_for_file(path,prefix)
    elif(os.path.isdir(path)):
        expr = re.compile("^"+prefix+"_.*.json$")
        paths = [os.path.join(path,f) for f in os.listdir(path) if re.match(expr,f)]
        result = []
        for p in paths:
            result = result + create_targets_for_file(p,prefix)
        return result
    else:
        return []

# Validates a CMOR target, skipping those that do not make any sense
def validate_target(target):
    minstr = getattr(target,valid_min_key,"").strip()
    maxstr = getattr(target,valid_max_key,"").strip()
    min = float(minstr) if minstr else -float("inf")
    max = float(maxstr) if maxstr else float("inf")
    if(min == max):
        log.error("The target variable %s in table %s has invalid bounds...skipping this target" % (target.variable,target.table))
        return False
    return True
