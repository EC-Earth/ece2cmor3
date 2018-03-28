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
   #logging.info("File %s written" % opath)


def write_varlist_ascii(targets,opath):
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    ofile = open(opath,'w')
    ofile.write('{:10} {:20} {:5} {:40} {:95} {:60} {:20} {} {}'.format('table', 'variable', 'prio', 'dimensions', 'long_name', 'list of MIPs which request this variable', 'comment_author', 'comment', '\n'))
    for k,vlist in tgtgroups.iteritems():
        ofile.write('{}'.format('\n'))
        for tgtvar in vlist:
            ofile.write('{:10} {:20} {:5} {:40} {:95} {:60} {:20} {} {}'.format(tgtvar.table, tgtvar.variable, tgtvar.priority, getattr(tgtvar,"dimensions","unknown"), getattr(tgtvar,"long_name","unknown"), tgtvar.mip_list, getattr(tgtvar,"comment_author",""), getattr(tgtvar,"ecearth_comment",""), '\n'))
    ofile.close()


def write_varlist_excel(targets,opath):
    import xlsxwriter
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    workbook = xlsxwriter.Workbook(opath)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:A', 10)  # Adjust the column width of column A
    worksheet.set_column('B:B', 15)  # Adjust the column width of column B
    worksheet.set_column('C:C',  4)  # Adjust the column width of column C
    worksheet.set_column('D:D', 35)  # Adjust the column width of column D
    worksheet.set_column('E:E', 80)  # Adjust the column width of column E
    worksheet.set_column('F:F',  4)  # Adjust the column width of column F
    worksheet.set_column('G:G', 80)  # Adjust the column width of column G
    worksheet.set_column('H:H', 15)  # Adjust the column width of column H
    worksheet.set_column('I:I',200)  # Adjust the column width of column I
    worksheet.set_column('J:J', 80)  # Adjust the column width of column J

    bold = workbook.add_format({'bold': True})   # Add a bold format

    worksheet.write(0, 0, 'Table', bold)
    worksheet.write(0, 1, 'variable', bold)
    worksheet.write(0, 2, 'prio', bold)
    worksheet.write(0, 3, 'Dimension format of variable', bold)
    worksheet.write(0, 4, 'variable long name', bold)
    worksheet.write(0, 5, 'link', bold)
    worksheet.write(0, 6, 'comment', bold)
    worksheet.write(0, 7, 'comment author', bold)
    worksheet.write(0, 8, 'extensive variable description', bold)
    worksheet.write(0, 9, 'list of MIPs which request this variable', bold)

    row_counter = 1
    for k,vlist in tgtgroups.iteritems():
        worksheet.write(row_counter, 0, '')
        row_counter += 1
        for tgtvar in vlist:
            worksheet.write(row_counter, 0, tgtvar.table)
            worksheet.write(row_counter, 1, tgtvar.variable)
            worksheet.write(row_counter, 2, tgtvar.priority)
            worksheet.write(row_counter, 3, getattr(tgtvar,"dimensions","unknown"))
            worksheet.write(row_counter, 4, getattr(tgtvar,"long_name","unknown"))
            worksheet.write(row_counter, 5, '=HYPERLINK("' + 'http://clipc-services.ceda.ac.uk/dreq/u/' + getattr(tgtvar,"vid","unknown") + '.html","web")')
            worksheet.write(row_counter, 6, getattr(tgtvar,"ecearth_comment",""))
            worksheet.write(row_counter, 7, getattr(tgtvar,"comment_author",""))
            worksheet.write(row_counter, 8, getattr(tgtvar,"comment","unknown"))
            worksheet.write(row_counter, 9, tgtvar.mip_list)
            row_counter += 1
    workbook.close()
    logging.info(" Writing the excel file: %s" % opath)


# Main program
def main():

    parser = argparse.ArgumentParser(description = "Validate input variable list against CMIP tables")
    parser.add_argument("--vars",   metavar = "FILE",   type = str, required = True, help = "File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    parser.add_argument("--tabdir", metavar = "DIR",    type = str, default = ece2cmorlib.table_dir_default, help = "Cmorization table directory")
    parser.add_argument("--tabid",  metavar = "PREFIX", type = str, default = ece2cmorlib.prefix_default, help = "Cmorization table prefix string")
    parser.add_argument("--output", metavar = "FILE",   type = str, default = None, help = "Output path to write variables to")
    parser.add_argument("--withouttablescheck", action = "store_true", default = False, help = "Ignore variable tables when performing var checking")
    parser.add_argument("-v", "--verbose", action = "store_true", default = False, help = "Write xlsx and ASCII files with verbose output (suppress the related terminal messages as the content of these files contain this information)")
    parser.add_argument("-a", "--atm", action = "store_true", default = False, help = "Run exclusively for atmosphere variables")
    parser.add_argument("-o", "--oce", action = "store_true", default = False, help = "Run exclusively for ocean variables")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default,mode = ece2cmorlib.PRESERVE,tabledir = args.tabdir,tableprefix = args.tabid)

    # Fix conflicting flags
    procatmos,prococean = not args.oce,not args.atm
    if(not procatmos and not prococean):
        procatmos,prococean = True,True

    # Configure task loader:
    taskloader.skip_tables = args.withouttablescheck

    # Load the variables as task targets:
    loadedtargets,ignoredtargets,identifiedmissingtargets,missingtargets = taskloader.load_targets(args.vars,load_atm_tasks = procatmos,load_oce_tasks = prococean, silent = args.verbose)

    if(args.output):
        output_dir = os.path.dirname(args.output)
        if(not os.path.isdir(output_dir)):
            if(output_dir != ''): os.makedirs(output_dir)
        write_varlist(loadedtargets,args.output + ".available.json")
        if(args.verbose):
            write_varlist_ascii(loadedtargets           ,args.output + ".available.txt")
           #write_varlist_ascii(ignoredtargets          ,args.output + ".ignored.txt")
           #write_varlist_ascii(identifiedmissingtargets,args.output + ".identifiedmissing.txt")
            write_varlist_ascii(missingtargets          ,args.output + ".missing.txt")

            write_varlist_excel(loadedtargets           ,args.output + ".available.xlsx")
            write_varlist_excel(ignoredtargets          ,args.output + ".ignored.xlsx")
            write_varlist_excel(identifiedmissingtargets,args.output + ".identifiedmissing.xlsx")
            write_varlist_excel(missingtargets          ,args.output + ".missing.xlsx")

    # Finishing up
    ece2cmorlib.finalize_without_cmor()

if __name__ == "__main__":
    main()
