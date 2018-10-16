#!/usr/bin/env python

# Call this script e.g. by:
#  ./drq2ppt.py --vars cmip6-data-request/cmip6-data-request-m=CMIP-e=CMIP-t=1-p=1/cmvme_CMIP_piControl_1_1.xlsx

import argparse
import logging
import re

import f90nml

from ece2cmor3 import ece2cmorlib, taskloader, cmor_source, cmor_target, cmor_utils, components

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Logger construction
log = logging.getLogger(__name__)


# Determines the ifs output period for given task (in hours)
def get_output_freq(task):
    if task.target.frequency == "fx":
        return 0
    if task.target.frequency.startswith("subhr"):
        return -1
    regex = re.search("^[0-9]+hr*", task.target.frequency)
    if regex:
        return int(regex.group(0)[:-2])
    return get_sample_freq(task)


# Determines the ifs output frequency for daily/monthly variables. By default
# 2D variables are requested on 3-hourly basis and 3D variables on 6-hourly basis.
def get_sample_freq(task):
    axis, levs = cmor_target.get_z_axis(task.target)
    if axis in cmor_target.model_axes + cmor_target.pressure_axes + cmor_target.height_axes:
        return 6
    else:
        return 3


# Writes a set of input IFS files for the requested tasks
def write_ppt_files(tasks):
    freqgroups = cmor_utils.group(tasks, get_output_freq)
    for freq1 in freqgroups:
        for freq2 in freqgroups:
            if freq2 > freq1 and freq2 % freq1 == 0:
                freqgroups[freq2] = freqgroups[freq1] + freqgroups[freq2]
    for freq in freqgroups:
        mfp2df, mfpphy, mfp3dfs, mfp3dfp, mfp3dfv = [], [], [], [], []
        alevs, plevs, hlevs = [], [], []
        for task in freqgroups[freq]:
            zaxis, levs = cmor_target.get_z_axis(task.target)
            root_codes = task.source.get_root_codes()
            if not zaxis:
                for code in root_codes:
                    if code in cmor_source.ifs_source.grib_codes_3D:
                        log.warning("3D grib code %s used in 2D cmor-target %s..."
                                    "assuming this is on model levels" % (str(code), task.target.variable))
                        mfp3dfs.append(code)
                    elif code in cmor_source.ifs_source.grib_codes_2D_dyn:
                        log.info("Adding grib code %s to MFP2DF %dhr ppt file for variable "
                                 "%s in table %s" % (str(code), freq, task.target.variable, task.target.table))
                        mfp2df.append(code)
                    elif code in cmor_source.ifs_source.grib_codes_2D_phy:
                        log.info("Adding grib code %s to MFPPHY %dhr ppt file for variable "
                                 "%s in table %s" % (str(code), freq, task.target.variable, task.target.table))
                        mfpphy.append(code)
                    else:
                        log.error("Unknown IFS grib code %s skipped" % str(code))
            else:
                for code in root_codes:
                    if code in cmor_source.ifs_source.grib_codes_3D:
                        if zaxis in cmor_target.model_axes:
                            log.info("Adding grib code %s to MFP3DFS %dhr ppt file for variable "
                                     "%s in table %s" % (str(code), freq, task.target.variable, task.target.table))
                            mfp3dfs.append(code)
                            alevs.extend(levs)
                        elif zaxis in cmor_target.pressure_axes:
                            log.info("Adding grib code %s to MFP3DFP %dhr ppt file for variable "
                                     "%s in table %s" % (str(code), freq, task.target.variable, task.target.table))
                            mfp3dfp.append(code)
                            plevs.extend(levs)
                        elif zaxis in cmor_target.height_axes:
                            log.info("Adding grib code %s to MFP3DFV %dhr ppt file for variable "
                                     "%s in table %s" % (str(code), freq, task.target.variable, task.target.table))
                            mfp3dfv.append(code)
                            hlevs.extend(levs)
                        else:
                            log.error("Axis type %s unknown, adding grib code %s"
                                      "to model level variables" % (zaxis, str(code)))
                    elif code in cmor_source.ifs_source.grib_codes_2D_dyn:
                        mfp2df.append(code)
                    elif code in cmor_source.ifs_source.grib_codes_2D_phy:
                        mfpphy.append(code)
                    else:
                        log.error("Unknown IFS grib code %s skipped" % str(code))
        # Always add the geopotential, recommended by ECMWF
        if cmor_source.grib_code(129) not in mfp3dfs:
            mfp2df.append(cmor_source.grib_code(129))
        # Always add the surface pressure, recommended by ECMWF
        mfpphy.append( cmor_source.grib_code(134))
        # Always add the logarithm of surface pressure, recommended by ECMWF
        mfp2df.append( cmor_source.grib_code(152))
        mfp2df = sorted(list(map(lambda c: c.var_id if c.tab_id == 128 else c.__hash__(), set(mfp2df))))
        mfpphy = sorted(list(map(lambda c: c.var_id if c.tab_id == 128 else c.__hash__(), set(mfpphy))))
        mfp3dfs = sorted(list(map(lambda c: c.var_id if c.tab_id == 128 else c.__hash__(), set(mfp3dfs))))
        mfp3dfp = sorted(list(map(lambda c: c.var_id if c.tab_id == 128 else c.__hash__(), set(mfp3dfp))))
        mfp3dfv = sorted(list(map(lambda c: c.var_id if c.tab_id == 128 else c.__hash__(), set(mfp3dfv))))
        plevs = sorted(list(set([float(s) for s in plevs])))[::-1]
        hlevs = sorted(list(set([float(s) for s in hlevs])))
        namelist = {"CFPFMT": "MODEL"}
        if any(mfp2df):
            namelist["NFP2DF"] = len(mfp2df)
            namelist["MFP2DF"] = mfp2df
        if any(mfpphy):
            namelist["NFPPHY"] = len(mfpphy)
            namelist["MFPPHY"] = mfpphy
        if any(mfp3dfs):
            namelist["NFP3DFS"] = len(mfp3dfs)
            namelist["MFP3DFS"] = mfp3dfs
            namelist["NRFP3S"] = -1
        if any(mfp3dfp):
            namelist["NFP3DFP"] = len(mfp3dfp)
            namelist["MFP3DFP"] = mfp3dfp
            namelist["RFP3P"] = plevs
        if any(mfp3dfs):
            namelist["NFP3DFV"] = len(mfp3dfv)
            namelist["MFP3DFV"] = mfp3dfv
            namelist["RFP3V"] = hlevs
        nml = f90nml.Namelist({"NAMFPC": namelist})
        nml.uppercase, nml.end_comma = True, True
        f90nml.write(nml, "pptdddddd%04d" % (100 * freq,))
        if freq == 6:
            mfpphy.extend([129, 172])
            mfpphy = sorted(list(set(mfpphy)))
            namelist["MFPPHY"] = mfpphy
            namelist["NFPPHY"] = len(mfpphy)
            nml = f90nml.Namelist({"NAMFPC": namelist})
            nml.uppercase, nml.end_comma = True, True
            f90nml.write(nml, "ppt0000000000")


# Main program
def main():
    parser = argparse.ArgumentParser(description="Create IFS ppt files for given data request")
    parser.add_argument("--vars", metavar="FILE", type=str, required=True,
                        help="File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default, mode=ece2cmorlib.PRESERVE, tabledir=args.tabdir,
                                        tableprefix=args.tabid)

    # Load only atmosphere variables as task targets:
    active_components = {component: False for component in components.models}
    active_components["ifs"] = True
    taskloader.load_targets(args.vars, active_components=active_components)

    # Write the IFS input files
    write_ppt_files(ece2cmorlib.tasks)

    # Finishing up
    ece2cmorlib.finalize_without_cmor()


if __name__ == "__main__":
    main()
