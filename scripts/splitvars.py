#!/usr/bin/env python

import sys
import os.path
import argparse
import json
from ece2cmor3 import ece2cmorlib
from ece2cmor3 import ece2cmor
from ece2cmor3 import jsonloader
from ece2cmor3 import cmor_target
from ece2cmor3 import cmor_task

frequencies = {"fx":float("inf"),"yr":8640.,"mon":720.,"day":24.,"6hr":6.,"3hr":3.,"hr":1.,"subhr":0.2}

def get_numlevs(target,modlevs):
    zdims = getattr(target,"z_dims",[])
    if(not any(zdims)):
        return 1
    axisname = zdims[0]
    if(axisname == "alevel"):
        return modlevs
    if(axisname == "alevhalf"):
        return modlevs - 1
    axisinfos = cmor_target.get_axis_info(target.table)
    axisinfo = axisinfos.get(axisname,None)
    if(not axisinfo):
        log.error("Could not retrieve information for axis %s in table %s" % (axisname,target.table))
        return 1
    zlevs = axisinfo.get("requested",[])
    return len(zlevs) if zlevs else 1


def get_numtims(target):
    freq = target.frequency
    hrs = frequencies.get(freq,float("inf"))
    return 720./hrs

def get_weight(task,modlevs):
    return get_numlevs(task.target,modlevs)*get_numtims(task.target)

def balance_tasks(tasklist,ngroups,modlevs):
    result = [[] for i in xrange(ngroups)]
    resultweights = [0 for i in xrange(ngroups)]
    for task in tasklist:
        j = resultweights.index(min(resultweights))
        result[j].append(task)
        resultweights[j] += get_weight(task,modlevs)
    return result

def write_varlist(tasklist,ofile):
    d = {}
    for task in tasklist:
        tgt = task.target
        if(tgt.table in d):
            d[tgt.table].append(tgt.variable)
        else:
            d[tgt.table] = [tgt.variable]
    with open(ofile,"w") as output:
        json.dump(d,output,indent = 4,separators = (',', ': '))

def splitvars(varlist,ngroups,modlevs,tabid):
    ece2cmorlib.initialize(tableprefix = tabid)
    jsonloader.load_targets(varlist)
    fname = os.path.splitext(os.path.basename(varlist))[0]
    taskgroups = balance_tasks(ece2cmorlib.tasks,ngroups,modlevs)
    i = 0
    for tasklist in taskgroups:
        i += 1
        write_varlist(tasklist,fname + "_" + str(i) + ".json")

def main(args):

    parser = argparse.ArgumentParser(description = "Load-balanced splitter of variable lists",
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("varlist",metavar = "FILE",   type = str, help = "Input filepath")
    parser.add_argument("groups", metavar = "N",      type = int, help = "Number of groups to split in")
    parser.add_argument("--levs", metavar = "N",      type = int, default = 100,     help = "Number of model levels")
    parser.add_argument("--tabid",metavar = "PREFIX", type = str, default = "CMIP6", help = "Cmorization table prefix string",choices = ["CMIP6","PRIMAVERA"])

    args = parser.parse_args()

    splitvars(args.varlist,args.groups,args.levs,args.tabid)

if __name__ == "__main__":
    main(sys.argv[1:])
