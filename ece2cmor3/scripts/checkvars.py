#!/usr/bin/env python

import argparse
import json
import logging
import sys
import os
import re

from ece2cmor3 import ece2cmorlib, taskloader, cmor_utils, components

# Logging configuration
##logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logformat   =             "%(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)

# Logger construction
log = logging.getLogger(__name__)


# Converts the input fortran variable namelist file to json
def write_varlist(targets, opath):
    tgtgroups = cmor_utils.group(targets, lambda t: t.table)
    tgtdict = {k: [t.variable for t in tgtgroups[k]] for k in list(tgtgroups.keys())}
    with open(opath, 'w') as ofile:
        json.dump(tgtdict, ofile, indent=4, separators=(',', ': '))
        ofile.write('\n')  # Add newline at the end of the json file because the python json package doesn't do this.
        ofile.close()
    logging.info('Writing the json  file: {:}'.format(opath))

# Check whether an attribute has a None value, if so replace the None value by an empty string:
def check_attribute_for_none_value(object_name, attribute_name, opath):
    if getattr(object_name, attribute_name, "") == None:
    #logging.info('An empty string is written for {:15} in {:6} {:10} in {:}'.format(attribute_name, object_name.table, object_name.variable, opath))
     logging.info('An empty string is written for {:15} in {:6} {:10} in {:}'.format(attribute_name, object_name.table, object_name.variable, re.sub(r'/.*/', '/*/', opath)))
     # Replace the None value by an empty string:
     setattr(object_name, attribute_name , "")

def tweakedorder_table_realm(iterable_object):           # From: https://clipc-services.ceda.ac.uk/dreq/index/miptable.html
    if   iterable_object == 'fx'          : return  1    #  fx           Fixed variables [fx] (8 variables)
    elif iterable_object == '3hr'         : return  2    #  3hr          3-hourly data [3hr] (23 variables)
    elif iterable_object == '6hrLev'      : return  3    #  6hrLev       6-hourly data on atmospheric model levels [6hr] (8 variables)
    elif iterable_object == '6hrPlev'     : return  4    #  6hrPlev      6-hourly atmospheric data on pressure levels (time mean) [6hr] (17 variables)
    elif iterable_object == '6hrPlevPt'   : return  5    #  6hrPlevPt    6-hourly atmospheric data on pressure levels (instantaneous) [6hr] (37 variables)
    elif iterable_object == 'day'         : return  6    #  day          Daily Data (extension - contains both atmospheric and oceanographic data) [day] (38 variables)
    elif iterable_object == 'Amon'        : return  7    #  Amon         Monthly atmospheric data [mon] (75 variables)
    elif iterable_object == 'Ofx'         : return  8    #  Ofx          Fixed ocean data [fx] (9 variables)
    elif iterable_object == 'Oday'        : return  9    #  Oday         Daily ocean data [day] (7 variables)
    elif iterable_object == 'Omon'        : return 10    #  Omon         Monthly ocean data [mon] (292 variables)
    elif iterable_object == 'Oyr'         : return 11    #  Oyr          Annual ocean variables [yr] (122 variables)
    elif iterable_object == 'Odec'        : return 12    #  Odec         Decadal ocean data [decadal] (30 variables)
    elif iterable_object == 'Oclim'       : return 13    #  Oclim        Monthly climatologies of ocean data [monClim] (34 variables)
    elif iterable_object == 'SIday'       : return 14    #  SIday        Daily sea-ice data [day] (9 variables)
    elif iterable_object == 'SImon'       : return 15    #  SImon        Monthly sea-ice data [mon] (89 variables)
    elif iterable_object == 'Lmon'        : return 16    #  Lmon         Monthly land surface and soil model fields [mon] (53 variables)
    elif iterable_object == 'LImon'       : return 17    #  LImon        Monthly fields for the terrestrial cryosphere [mon] (36 variables)
    elif iterable_object == 'CFsubhr'     : return 18    #  CFsubhr      Diagnostics for cloud forcing analysis at specific sites [subhr] (79 variables)
    elif iterable_object == 'CF3hr'       : return 19    #  CF3hr        3-hourly associated with cloud forcing [3hr] (64 variables)
    elif iterable_object == 'CFday'       : return 20    #  CFday        Daily data associated with cloud forcing [day] (36 variables)
    elif iterable_object == 'CFmon'       : return 21    #  CFmon        Monthly data associated with cloud forcing [mon] (57 variables)
    elif iterable_object == 'Efx'         : return 22    #  Efx          Fixed (extension) [fx] (16 variables)
    elif iterable_object == 'Esubhr'      : return 23    #  Esubhr       Sub-hourly (extension) [subhr] (33 variables)
    elif iterable_object == 'E1hr'        : return 24    #  E1hr         Hourly Atmospheric Data (extension) [1hr] (16 variables)
    elif iterable_object == 'E1hrClimMon' : return 25    #  E1hrClimMon  Diurnal Cycle [1hrClimMon] (5 variables)
    elif iterable_object == 'E3hr'        : return 26    #  E3hr         3-hourly (time mean, extension) [3hr] (19 variables)
    elif iterable_object == 'E3hrPt'      : return 27    #  E3hrPt       3-hourly (instantaneous, extension) [3hr] (48 variables)
    elif iterable_object == 'E6hrZ'       : return 28    #  E6hrZ        6-hourly Zonal Mean (extension) [6hr] (3 variables)
    elif iterable_object == 'Eday'        : return 29    #  Eday         Daily (time mean, extension) [day] (123 variables)
    elif iterable_object == 'EdayZ'       : return 30    #  EdayZ        Daily Zonal Mean (extension) [day] (15 variables)
    elif iterable_object == 'Emon'        : return 31    #  Emon         Monthly (time mean, extension) [mon] (331 variables)
    elif iterable_object == 'EmonZ'       : return 32    #  EmonZ        Monthly zonal means (time mean, extension) [mon] (25 variables)
    elif iterable_object == 'Eyr'         : return 33    #  Eyr          Daily (time mean, extension) [yr] (19 variables)
    elif iterable_object == 'AERfx'       : return 34    #  AERfx        Fixed atmospheric chemistry and aerosol data [fx] (0 variables)
    elif iterable_object == 'AERhr'       : return 35    #  AERhr        Hourly atmospheric chemistry and aerosol data [1hr] (5 variables)
    elif iterable_object == 'AERday'      : return 36    #  AERday       Daily atmospheric chemistry and aerosol data [day] (11 variables)
    elif iterable_object == 'AERmon'      : return 37    #  AERmon       Monthly atmospheric chemistry and aerosol data [mon] (126 variables)
    elif iterable_object == 'AERmonZ'     : return 38    #  AERmonZ      Monthly atmospheric chemistry and aerosol data [mon] (17 variables)
    elif iterable_object == 'IfxAnt'      : return 39    #  IfxAnt       Fixed fields on the Antarctic ice sheet [fx] (4 variables)
    elif iterable_object == 'IfxGre'      : return 40    #  IfxGre       Fixed fields on the Greenland ice sheet [fx] (4 variables)
    elif iterable_object == 'ImonAnt'     : return 41    #  ImonAnt      Monthly fields on the Antarctic ice sheet [mon] (27 variables)
    elif iterable_object == 'ImonGre'     : return 42    #  ImonGre      Monthly fields on the Greenland ice sheet [mon] (27 variables)
    elif iterable_object == 'IyrAnt'      : return 43    #  IyrAnt       Annual fields on the Antarctic ice sheet [yr] (33 variables)
    elif iterable_object == 'IyrGre'      : return 44    #  IyrGre       Annual fields on the Greenland ice sheet [yr] (33 variables)
    else:                                   return 45

def write_varlist_ascii(targets, opath, print_all_columns):
    tgtgroups = cmor_utils.group(targets, lambda t: t.table)
    ofile = open(opath, 'w')
    if print_all_columns:
     # In case the input data request is an xlsx file, all columns are printed:
     ofile.write('{:11} {:20} {:5} {:45} {:115} {:20} {:85} {:140} {:40} {}{}'.format(
                  'table', 'variable', 'prio', 'dimensions', 'long_name', 'unit','link',
                  'list of MIPs which request this variable', 'comment_author', 'comment', '\n'))
     for k  in sorted(tgtgroups.keys(), key=tweakedorder_table_realm):
         vlist = tgtgroups[k]
         ofile.write('{}'.format('\n'))
         for tgtvar in vlist:
             check_attribute_for_none_value(tgtvar, "priority"       , opath)
             check_attribute_for_none_value(tgtvar, "dimensions"     , opath)
             check_attribute_for_none_value(tgtvar, "long_name"      , opath)
             check_attribute_for_none_value(tgtvar, "mip_list"       , opath)
             check_attribute_for_none_value(tgtvar, "vid"            , opath)
             check_attribute_for_none_value(tgtvar, "comment_author" , opath)
             check_attribute_for_none_value(tgtvar, "ecearth_comment", opath)
             ofile.write('{:11} {:20} {:5} {:45} {:115} {:20} {:85} {:140} {:40} {}{}'.format(
                          tgtvar.table,
                          tgtvar.variable,
                          getattr(tgtvar, "priority"       , "unknown"),
                          getattr(tgtvar, "dimensions"     , "unknown"),
                          getattr(tgtvar, "long_name"      , "unknown"),
                          tgtvar.units,
                          'http://clipc-services.ceda.ac.uk/dreq/u/' + getattr(tgtvar, "vid", "unknown") + '.html',
                          getattr(tgtvar, "mip_list"       , "unknown"),
                          getattr(tgtvar, "comment_author" , ""       ),
                          getattr(tgtvar, "ecearth_comment", ""       ), '\n'))
    else:
     # In case the input data request is a json file, a reduced number of columns is printed:
     ofile.write('{:11} {:20} {:45} {:121} {:20} {}{}'.format('table', 'variable', 'dimensions', 'long_name', 'unit', 'comment', '\n'))
     for k  in sorted(tgtgroups.keys(), key=tweakedorder_table_realm):
         vlist = tgtgroups[k]
         ofile.write('{}'.format('\n'))
         for tgtvar in vlist:
             ofile.write('{:11} {:20} {:45} {:121} {:20} {}{}'.format(tgtvar.table,
                          tgtvar.variable,
                          getattr(tgtvar, "dimensions"     , "unknown"),
                          getattr(tgtvar, "long_name"      , "unknown"),
                          tgtvar.units,
                          getattr(tgtvar, "ecearth_comment", ""       ), '\n'))
    ofile.close()
    logging.info('Writing the ascii file: {:}'.format(opath))


def write_varlist_excel(targets, opath, with_pingfile):
    import xlsxwriter
    tgtgroups = cmor_utils.group(targets, lambda t: t.table)
    workbook = xlsxwriter.Workbook(opath)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:A',  10)     # Adjust the column width of column A
    worksheet.set_column('B:B',  15)     # Adjust the column width of column B
    worksheet.set_column('C:C',   4)     # Adjust the column width of column C
    worksheet.set_column('D:D',  35)     # Adjust the column width of column D
    worksheet.set_column('E:E',  80)     # Adjust the column width of column E
    worksheet.set_column('F:F',  15)     # Adjust the column width of column E
    worksheet.set_column('G:G',   4)     # Adjust the column width of column F
    worksheet.set_column('H:H',  80)     # Adjust the column width of column G
    worksheet.set_column('I:I',  15)     # Adjust the column width of column H
    worksheet.set_column('J:J', 200)     # Adjust the column width of column I
    worksheet.set_column('K:K',  80)     # Adjust the column width of column J
    if with_pingfile:
        worksheet.set_column('L:L',  28) # Adjust the column width of column L
        worksheet.set_column('M:M',  17) # Adjust the column width of column M
        worksheet.set_column('N:N', 100) # Adjust the column width of column N

    bold = workbook.add_format({'bold': True})  # Add a bold format

    worksheet.write(0, 0, 'Table'                                    , bold)
    worksheet.write(0, 1, 'variable'                                 , bold)
    worksheet.write(0, 2, 'prio'                                     , bold)
    worksheet.write(0, 3, 'Dimension format of variable'             , bold)
    worksheet.write(0, 4, 'variable long name'                       , bold)
    worksheet.write(0, 5, 'unit'                                     , bold)
    worksheet.write(0, 6, 'link'                                     , bold)
    worksheet.write(0, 7, 'comment'                                  , bold)
    worksheet.write(0, 8, 'comment author'                           , bold)
    worksheet.write(0, 9, 'extensive variable description'           , bold)
    worksheet.write(0, 10, 'list of MIPs which request this variable', bold)
    if with_pingfile:
        worksheet.write(0, 11, 'model component in ping file'        , bold)
        worksheet.write(0, 12, 'units as in ping file'               , bold)
        worksheet.write(0, 13, 'ping file comment'                   , bold)

    row_counter = 1
    for k  in sorted(tgtgroups.keys(), key=tweakedorder_table_realm):
        vlist = tgtgroups[k]
        worksheet.write(row_counter, 0, '')
        row_counter += 1
        for tgtvar in vlist:
            worksheet.write(row_counter, 0, tgtvar.table)
            worksheet.write(row_counter, 1, tgtvar.variable)
            worksheet.write(row_counter, 2, getattr(tgtvar, "priority"  , "unknown"))
            worksheet.write(row_counter, 3, getattr(tgtvar, "dimensions", "unknown"))
            worksheet.write(row_counter, 4, getattr(tgtvar, "long_name" , "unknown"))
            worksheet.write(row_counter, 5, tgtvar.units)
            worksheet.write(row_counter, 6, '=HYPERLINK("' + 'http://clipc-services.ceda.ac.uk/dreq/u/' +
                                            getattr(tgtvar, "vid", "unknown") + '.html","web")')
            worksheet.write(row_counter, 7, getattr(tgtvar, "ecearth_comment", ""       ))
            worksheet.write(row_counter, 8, getattr(tgtvar, "comment_author" , ""       ))
            worksheet.write(row_counter, 9, getattr(tgtvar, "comment"        , "unknown"))
            worksheet.write(row_counter, 10, getattr(tgtvar, "mip_list"      , "unknown"))
            if with_pingfile:
                worksheet.write(row_counter, 11, getattr(tgtvar, "model"      , ""))
                worksheet.write(row_counter, 12, getattr(tgtvar, "units"      , ""))
                worksheet.write(row_counter, 13, getattr(tgtvar, "pingcomment", ""))
            row_counter += 1
    workbook.close()
    logging.info('Writing the excel file: {:}'.format(opath))


# Main program
def main():
    parser = argparse.ArgumentParser(description="Validate input variable list against CMIP tables")
    parser.add_argument("--drq", metavar="FILE", type=str, required=True,
                        help="File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    cmor_utils.ScriptUtils.add_model_exclusive_options(parser, "checkvars")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")
    parser.add_argument("--output", metavar="FILE", type=str, default=None, help="Output path to write variables to")
    parser.add_argument("--withouttablescheck", action="store_true", default=False,
                        help="Ignore variable tables when performing var checking")
    parser.add_argument("--withping", action="store_true", default=False,
                        help="Read and write addition ping file fields")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Write xlsx and ASCII files with verbose output (suppress the related terminal messages "
                             "as the content of these files contain this information)")
    parser.add_argument("--asciionly", action="store_true", default=False,
                        help="Write the ascii file(s) only")
    cmor_utils.ScriptUtils.add_model_tabfile_options(parser)

    args = parser.parse_args()

    # Echo the exact call of the script in the log messages:
    logging.info('Running {:} with:\n\n {:} {:}\n'.format(parser.prog, parser.prog, ' '.join(sys.argv[1:])))
    # Print the values of all arguments in the log messages::
    logging.info('------  {} argument list:  ------'.format(parser.prog))
    for arg_key, arg_value in vars(parser.parse_args()).items(): logging.info('--{:18} = {:}'.format(arg_key, arg_value))
    logging.info('------  end {} argument list  ------\n'.format(parser.prog))

    if not os.path.isfile(args.drq):
        log.fatal('Error: Your data request file {:} cannot be found.'.format(args.drq))
        sys.exit('ERROR: Exiting {:}'.format(parser.prog))

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default, mode=ece2cmorlib.PRESERVE, tabledir=args.tabdir,
                                        tableprefix=args.tabid)

    active_components = cmor_utils.ScriptUtils.get_active_components(args)

    # Configure task loader:
    taskloader.skip_tables   = args.withouttablescheck
    taskloader.with_pingfile = args.withping

    # Load the variables as task targets:
    try:
        matches, omitted_targets = taskloader.load_drq(args.drq, check_prefs=False)
    except taskloader.SwapDrqAndVarListException as e:
        log.error(e.message)
        opt1, opt2 = "vars" if e.reverse else "drq", "drq" if e.reverse else "vars"
        log.error('It seems you are using the --{:} option where you should use the --{:} option for this file'.format(opt1, opt2))
        sys.exit('ERROR: Exiting {:}'.format(parser.prog))

    loaded = [t for m in active_components for t in matches[m]]
    ignored, identified_missing, missing, dismissed = taskloader.split_targets(omitted_targets)

    loaded_targets             = sorted(list(set(loaded)) , key=lambda tgt: (tgt.table, tgt.variable))
    ignored_targets            = sorted(list(set(ignored)), key=lambda tgt: (tgt.table, tgt.variable))
    identified_missing_targets = sorted(identified_missing, key=lambda tgt: (tgt.table, tgt.variable))
    missing_targets            = sorted(missing           , key=lambda tgt: (tgt.table, tgt.variable))

    if args.output:
        output_dir = os.path.dirname(args.output)
        if not os.path.isdir(output_dir):
            if output_dir != '':
                os.makedirs(output_dir)
        if not args.asciionly:
         write_varlist(loaded, args.output + ".available.json")
        if args.verbose:
            if not args.asciionly:
             write_varlist_excel(loaded_targets            , args.output + ".available.xlsx"        , args.withping)
             write_varlist_excel(ignored_targets           , args.output + ".ignored.xlsx"          , args.withping)
             write_varlist_excel(identified_missing_targets, args.output + ".identifiedmissing.xlsx", args.withping)
             write_varlist_excel(missing_targets           , args.output + ".missing.xlsx"          , args.withping)

            if args.drq[-4:] == 'xlsx':
             write_varlist_ascii(loaded_targets            , args.output + ".available.txt"        , True)
             write_varlist_ascii(ignored_targets           , args.output + ".ignored.txt"          , True)
             write_varlist_ascii(identified_missing_targets, args.output + ".identifiedmissing.txt", True)
             write_varlist_ascii(missing_targets           , args.output + ".missing.txt"          , True)
            else:
             write_varlist_ascii(loaded_targets            , args.output + ".available.txt"        , False)


    if False:
     # Add writing of a json data request formatted file which includes all available variables in order to provide a
     # single test which covers all identified & available variables. If this block is activated and the following is run:
     # ./determine-missing-variables.sh CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB CMIP 1 1
     # At least an equivalent json data request which covers all Core MIP requests is produced. However this does not
     # necessarily include all specific MIP requests. In fact it would be better to create a json data request equivalent
     # based on the ifspar.json.
     result = {}
     for model, targetlist in list(matches.items()):
         result[model] = {}
         for target in targetlist:
             table = target.table
             if table in result[model]:
                 result[model][table].append(target.variable)
             else:
                 result[model][table] = [target.variable]
    #with open(args.output + "-varlist-all-available.json", 'w') as ofile:
     with open("varlist-all.json", 'w') as ofile:
         json.dump(result, ofile, indent=4, separators=(',', ': '), sort_keys=True)
         ofile.write('\n')  # Add newline at the end of the json file because the python json package doesn't do this.
         ofile.close()

     # Finishing up
     ece2cmorlib.finalize_without_cmor()


if __name__ == "__main__":
    main()
