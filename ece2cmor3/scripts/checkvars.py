#!/usr/bin/env python

import sys
import os
import logging
import argparse
import json
from ece2cmor3 import ece2cmorlib,taskloader,cmor_source,cmor_utils

# Logging configuration
logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)

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
    ofile.write('{:10} {:20} {:5} {:40} {:95} {:20} {:60} {:20} {} {}'.format('table', 'variable', 'prio', 'dimensions', 'long_name', 'unit', 'list of MIPs which request this variable', 'comment_author', 'comment', '\n'))
    for k,vlist in tgtgroups.iteritems():
        ofile.write('{}'.format('\n'))
        for tgtvar in vlist:
            ofile.write('{:10} {:20} {:5} {:40} {:95} {:20} {:60} {:20} {} {}'.format(tgtvar.table, tgtvar.variable, tgtvar.priority, getattr(tgtvar,"dimensions","unknown"), getattr(tgtvar,"long_name","unknown"), tgtvar.units, tgtvar.mip_list, getattr(tgtvar,"comment_author",""), getattr(tgtvar,"ecearth_comment",""), '\n'))
    ofile.close()


def write_varlist_excel(targets,opath,with_pingfile):
    import xlsxwriter
    tgtgroups = cmor_utils.group(targets,lambda t:t.table)
    workbook = xlsxwriter.Workbook(opath)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:A', 10)  # Adjust the column width of column A
    worksheet.set_column('B:B', 15)  # Adjust the column width of column B
    worksheet.set_column('C:C',  4)  # Adjust the column width of column C
    worksheet.set_column('D:D', 35)  # Adjust the column width of column D
    worksheet.set_column('E:E', 80)  # Adjust the column width of column E
    worksheet.set_column('F:F', 15)  # Adjust the column width of column E
    worksheet.set_column('G:G',  4)  # Adjust the column width of column F
    worksheet.set_column('H:H', 80)  # Adjust the column width of column G
    worksheet.set_column('I:I', 15)  # Adjust the column width of column H
    worksheet.set_column('J:J',200)  # Adjust the column width of column I
    worksheet.set_column('K:K', 80)  # Adjust the column width of column J
    if with_pingfile:
     worksheet.set_column('L:L', 28) # Adjust the column width of column L
     worksheet.set_column('M:M', 17) # Adjust the column width of column M
     worksheet.set_column('N:N',100) # Adjust the column width of column N

    bold = workbook.add_format({'bold': True})   # Add a bold format

    worksheet.write(0, 0, 'Table', bold)
    worksheet.write(0, 1, 'variable', bold)
    worksheet.write(0, 2, 'prio', bold)
    worksheet.write(0, 3, 'Dimension format of variable', bold)
    worksheet.write(0, 4, 'variable long name', bold)
    worksheet.write(0, 5, 'unit', bold)
    worksheet.write(0, 6, 'link', bold)
    worksheet.write(0, 7, 'comment', bold)
    worksheet.write(0, 8, 'comment author', bold)
    worksheet.write(0, 9, 'extensive variable description', bold)
    worksheet.write(0,10, 'list of MIPs which request this variable', bold)
    if with_pingfile:
     worksheet.write(0,11, 'model component in ping file', bold)
     worksheet.write(0,12, 'units as in ping file', bold)
     worksheet.write(0,13, 'ping file comment', bold)

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
            worksheet.write(row_counter, 5, tgtvar.units)
            worksheet.write(row_counter, 6, '=HYPERLINK("' + 'http://clipc-services.ceda.ac.uk/dreq/u/' + getattr(tgtvar,"vid","unknown") + '.html","web")')
            worksheet.write(row_counter, 7, getattr(tgtvar,"ecearth_comment",""))
            worksheet.write(row_counter, 8, getattr(tgtvar,"comment_author",""))
            worksheet.write(row_counter, 9, getattr(tgtvar,"comment","unknown"))
            worksheet.write(row_counter,10, tgtvar.mip_list)
            if with_pingfile:
             worksheet.write(row_counter,11, getattr(tgtvar,"model",""))
             worksheet.write(row_counter,12, getattr(tgtvar,"units",""))
             worksheet.write(row_counter,13, getattr(tgtvar,"pingcomment",""))
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
    parser.add_argument("--withping", action = "store_true", default = False, help = "Read and write addition ping file fields")
    parser.add_argument("-v", "--verbose", action = "store_true", default = False, help = "Write xlsx and ASCII files with verbose output (suppress the related terminal messages as the content of these files contain this information)")

    parser.add_argument("--ifs",  action = "store_true", default = False, help = "Run exclusively for IFS (i.e. atmosphere) variables")
    parser.add_argument("--nemo", action = "store_true", default = False, help = "Run exclusively for NEMO (i.e. ocean) variables")
    parser.add_argument("--lpjg", action = "store_true", default = False, help = "Run exclusively for LPJ-Guess (i.e. vegetation) variables")
    parser.add_argument("--tm5" , action = "store_true", default = False, help = "Run exclusively for TM5 (i.e. atmospheric chemistry) variables")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default,mode = ece2cmorlib.PRESERVE,tabledir = args.tabdir,tableprefix = args.tabid)

    active_components = {"ifs": args.ifs, "nemo": args.nemo, "lpjg": args.lpjg, "tm5":args.tm5}
    if not any(active_components.values()):
        active_components = {"ifs": True, "nemo": True, "lpjg": True, "tm5": True}

    # Configure task loader:
    taskloader.skip_tables = args.withouttablescheck
    taskloader.with_pingfile = args.withping

    # Load the variables as task targets:
    loadedtargets,ignoredtargets,identifiedmissingtargets,missingtargets = taskloader.load_targets(args.vars,active_components=active_components, silent = args.verbose)

    if(args.output):
        output_dir = os.path.dirname(args.output)
        if(not os.path.isdir(output_dir)):
            if(output_dir != ''): os.makedirs(output_dir)
        write_varlist(loadedtargets,args.output + ".available.json")
        if(args.verbose):
            write_varlist_excel(loadedtargets           ,args.output + ".available.xlsx"        , args.withping)
            write_varlist_excel(ignoredtargets          ,args.output + ".ignored.xlsx"          , args.withping)
            write_varlist_excel(identifiedmissingtargets,args.output + ".identifiedmissing.xlsx", args.withping)
            write_varlist_excel(missingtargets          ,args.output + ".missing.xlsx"          , args.withping)

            write_varlist_ascii(loadedtargets           ,args.output + ".available.txt"        )
            write_varlist_ascii(ignoredtargets          ,args.output + ".ignored.txt"          )
            write_varlist_ascii(identifiedmissingtargets,args.output + ".identifiedmissing.txt")
            write_varlist_ascii(missingtargets          ,args.output + ".missing.txt"          )


    # Finishing up
    ece2cmorlib.finalize_without_cmor()

if __name__ == "__main__":
    main()
