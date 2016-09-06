from datetime import timedelta
import os
import re
import json

# Class for cmor target objects, which represent output variables.

class cmor_target(object):

    def __init__(self,var_id__,tab_id__):
        self.variable=var_id__
        self.table=tab_id__

# Derives the table id for the given file path

def get_table_id(filepath,prefix):
    fname=os.path.basename(filepath)
    regex=re.search("^"+prefix+"_.*.json",fname)
    if(not regex):
        raise Exception("Invalid cmor table file name encountered:",fname)
    return regex.group()[len(prefix)+1:len(fname)-5]

# Json file keys:

head_key="Header"
freq_key="frequency"
var_key="variable_entry"

def create_targets_for_file(filepath,prefix):
    tabid=get_table_id(filepath,prefix)
    s=open(filepath).read()
    data=json.loads(s)
    result=[]
    # TODO: Use case insensitive search here
    header=data[head_key]
    freq=header[freq_key]
    var_entries=data[var_key]
    for k,v in var_entries.iteritems():
        t=cmor_target(k,tabid)
        t.frequency=freq
        for k2,v2 in v.iteritems():
            setattr(t,k2,v2)
        result.append(t)
    return result

def create_targets(path,prefix):
    if(os.path.isfile(path)):
        return create_targets_for_file(path,prefix)
    elif(os.path.isdir(path)):
        # do something
    else:
        return []
