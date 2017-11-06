#!/usr/bin/env python

import sys
import os
import logging
import argparse
import json
from ece2cmor3 import ece2cmorlib,taskloader,cmor_source,cmor_utils

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Logger construction
log = logging.getLogger(__name__)


# Converts the input fortran variable namelist file to json
def write_varlist(targets,opath):
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    tgtdict = dict([k,[t.variable for t in v]] for k,v in tgtgroups.iteritems())
    with open(opath,'w') as ofile:
        json.dump(tgtdict,ofile,indent = 4,separators = (',', ': '))
    logging.info("File %s written" % opath)


def write_varlist_ascii(targets,opath):
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    ofile = open(opath,'w')
    ofile.write('{:10} {:40} {:20} {:95} {} {}'.format('table', 'dimensions', 'variable', 'long_name', 'comment', '\n'))
    for k,vlist in tgtgroups.iteritems():
        ofile.write('{}'.format('\n'))
        for tgtvar in vlist:
            ofile.write('{:10} {:40} {:20} {:95} {} {}'.format(tgtvar.table, getattr(tgtvar,"dimensions","unknown"), tgtvar.variable, getattr(tgtvar,"long_name","unknown"), getattr(tgtvar,"ignore_comment",""), '\n'))
    ofile.close()


def write_varlist_excel(targets,opath):
    import xlsxwriter
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    workbook = xlsxwriter.Workbook(opath)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:A', 10)  # Adjust the column width of column A
    worksheet.set_column('B:B', 35)  # Adjust the column width of column B
    worksheet.set_column('C:C', 15)  # Adjust the column width of column C
    worksheet.set_column('D:D', 80)  # Adjust the column width of column D
    worksheet.set_column('E:E', 80)  # Adjust the column width of column E

    bold = workbook.add_format({'bold': True})   # Add a bold format

    worksheet.write(0, 0, 'Table', bold)
    worksheet.write(0, 1, 'Dimension format of variable', bold)
    worksheet.write(0, 2, 'variable', bold)
    worksheet.write(0, 3, 'variable description', bold)
    worksheet.write(0, 4, 'comment', bold)
    row_counter = 1
    for k,vlist in tgtgroups.iteritems():
        worksheet.write(row_counter, 0, '')
        row_counter += 1
        for tgtvar in vlist:
            worksheet.write(row_counter, 0, tgtvar.table)
            worksheet.write(row_counter, 1, getattr(tgtvar,"dimensions","unknown"))
            worksheet.write(row_counter, 2, tgtvar.variable)
            worksheet.write(row_counter, 3, getattr(tgtvar,"long_name","unknown"))
            worksheet.write(row_counter, 4, getattr(tgtvar,"ignore_comment",""))
            row_counter += 1
    workbook.close()


# Main program
def main():

    parser = argparse.ArgumentParser(description = "Validate input variable list against CMIP tables")
    parser.add_argument("--vars",   metavar = "FILE",   type = str, required = True, help = "File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    parser.add_argument("--tabdir", metavar = "DIR",    type = str, default = ece2cmorlib.table_dir_default, help = "Cmorization table directory")
    parser.add_argument("--tabid",  metavar = "PREFIX", type = str, default = ece2cmorlib.prefix_default, help = "Cmorization table prefix string")
    parser.add_argument("--output", metavar = "FILE",   type = str, default = None, help = "Output path to write variables to")
    parser.add_argument("-v", "--verbose", action = "store_true", default = False, help = "Write ASCII file with verbose output")
    parser.add_argument("-a", "--atm", action = "store_true", default = False, help = "Run exclusively for atmosphere variables")
    parser.add_argument("-o", "--oce", action = "store_true", default = False, help = "Run exclusively for ocean variables")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize(ece2cmorlib.conf_path_default,mode = ece2cmorlib.PRESERVE,tabledir = args.tabdir,tableprefix = args.tabid)

    # Fix conflicting flags
    procatmos,prococean = not args.oce,not args.atm
    if(not procatmos and not prococean):
        procatmos,prococean = True,True

    # Load the variables as task targets:
    loadedtargets,ignoredtargets,missingtargets = taskloader.load_targets(args.vars,load_atm_tasks = procatmos,load_oce_tasks = prococean)

    if(args.output):
        ofile,fext = os.path.splitext(args.output)
        write_varlist(loadedtargets,ofile + ".available.json")
        write_varlist(ignoredtargets,ofile + ".ignored.json")
        write_varlist(missingtargets,ofile + ".missing.json")
        if(args.verbose):
            write_varlist_ascii(loadedtargets,ofile + ".available.txt")
            write_varlist_ascii(ignoredtargets,ofile + ".ignored.txt")
            write_varlist_ascii(missingtargets,ofile + ".missing.txt")

            write_varlist_excel(loadedtargets,ofile + ".available.xlsx")
            write_varlist_excel(ignoredtargets,ofile + ".ignored.xlsx")
            write_varlist_excel(missingtargets,ofile + ".missing.xlsx")

    # Finishing up
    ece2cmorlib.finalize()

if __name__ == "__main__":
    main()
