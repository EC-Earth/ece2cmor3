#!/usr/bin/env python

import traceback
import sys
import os
import logging
import optparse
import gribapi
import dateutil
import fixmonths

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
verbose = 1

def filter_record(msgid,files):
    levtype = gribapi.grib_get(msgid,"levelType")
    time = int(gribapi.grib_get(msgid,"dataTime"))
    code = int(gribapi.grib_get(msgid,"paramId"))

    if(levtype in ["ml","pl","99"]):
        if(time % 600 == 0):
            gribapi.grib_write(msgid,files[1])
        lev = float(gribapi.grib_get(msgid,"level"))
        if((code,lev) in [(152,1000.),(131,850.),(132,850.)]):
            gribapi.grib_write(msgid,files[0])
    else:
        if(code == 129): return
        if(code != 3):
            gribapi.grib_write(msgid,files[0])
        else:
            gribapi.grib_write(msgid,files[1])
        if(code == 134 and (time % 600 == 0)):
            gribapi.grib_write(msgid,files[1])


def main(args):

    parser = optparse.OptionParser(usage = "usage: %prog [options] file")
    parser.add_option("-p","--prev",  dest = "pfile", help = "Previous month grib file", default = None)
    parser.add_option("-o","--out",   dest = "odir", help = "Output directory", default = None)

    (opt,args) = parser.parse_args()

    ifile = args[0]

    if(len(args)<1):
        log.error("No argument grib file given...aborting")
        return 1
    elif(len(args)>1):
        log.warning("Multiple grib files given...will take first")

    if(not (os.path.isfile(ifile) or os.path.islink(ifile))):
        log.error("Invalid input file path %s given" % ifile)
        return 1
    ifile = os.path.abspath(ifile)
    log.info("Found input file: %s",ifile)

    date = fixmonths.get_ifs_date(ifile)
    if(date == None):
        log.error("Could not detect year and month from input file %s" % ifile)
        return 1
    month = date.month
    log.info("Processing month %s",str(month))

    pfile = opt.pfile
    if(not pfile):
        idir = os.path.dirname(ifile)
        ifilename = os.path.basename(ifile)
        date = fixmonths.get_ifs_date(ifile)
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

    odir = opt.odir
    if(not odir):
        odir = os.getcwd()
    if(not os.path.exists(odir)):
        log.error("Output directory %s does not exist" % odir)
        return 1
    path3hr,path6hr = os.path.join(odir,"3hr"),os.path.join(odir,"6hr")
    for dirname in [path3hr,path6hr]:
        if(not os.path.exists(dirname)): os.makedirs(dirname)
    file3hr,file6hr = os.path.join(path3hr,os.path.basename(ifile)),os.path.join(path6hr,os.path.basename(ifile))
    log.info("Producing output files %s and %s" % (file3hr,file6hr))

    try:
        fixmonths.timeshift = 3 if pfile else 0
        print "Merging months..."
        fixmonths.merge_months(month,pfile,ifile,[file3hr,file6hr],filter_record)
        for fpath in [file3hr,file6hr]:
            if os.stat(fpath).st_size == 0: os.remove(fpath)
    except gribapi.GribInternalError,err:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        else:
            log.error(sys.stderr,err.msg)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
