#!/usr/bin/env python

import traceback
import sys
import numpy
from gribapi import *

VERBOSE=1 # verbose error reporting

def example(ifile,ofile,levels):
    """
    Encoding of the pv coefficients.
    """
    fin = open(ifile)
    fout = open(ofile,'w')
    i=0
    while True:
        gid = grib_new_from_file(fin)
        if(not gid): break
        if(grib_get(gid,"typeOfLevel") == "hybrid"):
            nlevs = int(grib_get(gid,"numberOfVerticalCoordinateValues"))/2 - 1
            frac = nlevs/levels
            if(frac > 0):
                indices = numpy.arange(nlevs,1,-frac)[::-1]
                lev = int(grib_get(gid,"level"))
                code = int(grib_get(gid,"indicatorOfParameter"))
                if(code not in [134,152]):
                    if(lev not in indices): continue
                    newlev = indices.tolist().index(lev)
                    grib_set(gid,"level",newlev)
                pv = grib_get_array(gid,"pv")
                newpv = [pv[0]]
                for i in indices:
                    newpv.append(pv[i-1])
                newpv.append(pv[nlevs])
                for i in indices:
                    newpv.append(pv[nlevs+i-1])
                grib_set_array(gid,"pv",newpv)
                grib_set(gid,"numberOfVerticalCoordinateValues",2*(levels + 1))
        grib_write(gid,fout)
        grib_release(gid)
    fout.close()
    fin.close()

def main(ifile,ofile,levels):
    try:
        example(ifile,ofile,int(levels))
    except GribInternalError,err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            print >>sys.stderr,err.msg
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1],sys.argv[2],sys.argv[3]))
