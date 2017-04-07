#!/usr/bin/env python

import traceback
import sys
import os
import re
import numpy
import json
import datetime
import dateutil.relativedelta
import optparse
import logging
from gribapi import *

VERBOSE=1 # verbose error reporting
accum_key = "ACCUMFLD"
timeshift = 0
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Utility to make grib tuple of codes from string
def make_grib_tuple(s):
    codes = s.split('.')
    return (int(codes[0]),int(codes[1]))

# Function reading the file with grib-codes of accumulated fields
def load_accum_codes(path):
    global accum_key
    data = json.loads(open(path).read())
    if(accum_key in data):
        return map(make_grib_tuple,data[accum_key])
    else:
        return []

def get_ifs_date(filepath):
    fname=os.path.basename(filepath)
    regex=re.search("\+[0-9]{6}",fname)
    if(not regex):
        log.error("Unable to parse time stamp from ifs file name %s" % fname)
        return None
    ss=regex.group()[1:]
    return datetime.datetime.strptime(ss,"%Y%m").date()

# Function writing a grib record
def write_record(msgid,files):
    grib_write(msgid,files[0])

# Grib codes of accumulated fields
accum_codes = load_accum_codes(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","resources","grib_codes.json"))

# Main function merging data from two consecutive monthly files
def merge_months(month,prevmonfile,curmonfile,ofiles,writer = write_record):
    if(isinstance(ofiles,list)):
        fouts = [open(ofile,'w') for ofile in ofiles]
    else:
        fouts = [open(ofiles,'w')]
    ifiles = [prevmonfile,curmonfile]
    merge_funcs = [merge_prev_months,merge_cur_months]
    if(prevmonfile):
        fin = open(prevmonfile)
        merge_prev_months(month,fin,fouts,writer)
        fin.close()
    if(curmonfile):
        fin = open(curmonfile)
        merge_cur_months(month,fin,fouts,writer)
        fin.close()
    for fout in fouts:
        fout.close()

# Function writing instantaneous midnight fields from previous month
def merge_prev_months(month,fin,fouts,writer):
    while True:
        gid = grib_new_from_file(fin)
        if(not gid): break
        date = int(grib_get(gid,"dataDate"))
        mon = (date % 10000)/100
        if(mon == month):
            code = make_grib_tuple(grib_get(gid,"param"))
            if(code in accum_codes): continue
            writer(gid,fouts)
        grib_release(gid)

# Function writing data from current monthly file, optionally shifting accumulated fields
# and skipping next month instantaneous fields
def merge_cur_months(month,fin,fouts,writer):
    while True:
        gid = grib_new_from_file(fin)
        if(not gid): break
        date = int(grib_get(gid,"dataDate"))
        mon = (date % 10**4)/10**2
        if(mon not in [month,(month + 1)%12]): continue
        curdate = datetime.date(date / 10**4,mon,date % 10**2) if timeshift else None
        code = make_grib_tuple(grib_get(gid,"param"))
        if(code in accum_codes and timeshift):
            newtime = int(grib_get(gid,"dataTime")) - 100 * timeshift
            newdate = date
            if(newtime < 0):
                prevdate = curdate - datetime.timedelta(days = 1)
                mon = prevdate.month
                newdate = prevdate.year*10**4 + mon*10**2 + prevdate.day
                newtime = 2400 + newtime
            grib_set(gid,"dataDate",newdate)
            grib_set(gid,"dataTime",newtime)
        if(mon == month):
            writer(gid,fouts)
        grib_release(gid)

def main(args):

    global timeshift

    parser = optparse.OptionParser(usage = "usage: %prog [options] file")
    parser.add_option("-p","--prev",  dest = "pfile", help = "Previous month grib file", default = None)
    parser.add_option("-d","--shift", dest = "shift", help = "Time shift (in hrs) for cumulative fields", default = "0")
    parser.add_option("-o","--out",   dest = "ofile", help = "Output file name",default = None)

    (opt,args) = parser.parse_args()

    ifile = args[0]
    if(not (os.path.isfile(ifile) or os.path.islink(ifile))):
        log.error("Invalid input file path %s given" % ifile)
        return 1
    ifile = os.path.abspath(ifile)
    log.info("Found input file: %s",ifile)
    date = get_ifs_date(ifile)
    if(date == None):
        log.error("Could not detect year and month from input file %s" % ifile)
        return 1
    month = date.month
    log.info("Processing month %s",str(month))

    pfile = opt.pfile
    if(not pfile):
        idir = os.path.dirname(ifile)
        ifilename = os.path.basename(ifile)
        date = get_ifs_date(ifile)
        if(date == None): return 1
        prevdate = (date - dateutil.relativedelta.relativedelta(months=1))
        pfile = os.path.join(idir,ifilename.replace(date.strftime("%Y%m"),prevdate.strftime("%Y%m")))
        if(not (os.path.isfile(pfile) or os.path.islink(pfile))):
            log.warning("Previous month grib file %s could not be found...running without" % pfile)
            pfile = None
    elif(not (os.path.isfile(pfile) or os.path.islink(pfile))):
        log.error("Previous month grib file %s could not be found." % pfile)
        return 1
    if(pfile): log.info("Using previous month data from %s" % pfile)

    shift = int(opt.shift)
    if(shift < 0 or shift >= 24):
        log.error("Invalid time shift %s given: please use a non-negative integer < 24" % str(shift))
        return 1
    if(shift): log.info("Using time shift for accumulated fields of %s" % str(shift))

    ofile = opt.ofile
    if(not ofile):
        ofile = os.path.abspath(os.path.join(".",os.path.basename(ifile)))
    if(os.path.exists(ofile)):
        log.error("Output path %s already exists")
        return 1
    log.info("Producing output file %s" % ofile)

    try:
        timeshift = shift
        merge_months(month,pfile,ifile,ofile)
    except GribInternalError,err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            print >>sys.stderr,err.msg
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
