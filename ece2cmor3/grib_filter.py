import logging
import gribapi
import cmor_utils

gridpoint_file = None
prev_gridpoint_file = None
spectral_file = None
prev_spectral_file = None

temp_dir = None

def initialize(gpfile,shfile,tmpdir):
    global gridpoint_file,prev_gridpoint_file,spectral_file,prev_spectral_file,temp_dir
    gridpoint_file = gpfile
    spectral_file = shfile
    temp_dir = tmpdir
    prev_gridpoint_file,prev_spectral_file = get_prev_files(gridpoint_file)
    if(not prev_spectral_file or not prev_gridpoint_file):
        return False


def get_prev_files(gpfile):
    log.info("Searching for previous month file of %s" % gpfile)
    date = cmor_utils.get_ifs_date(gpfile)
    prevdate = date - dateutil.relativedelta(month = 1)
    ifsoutputdir = os.path.abspath(os.path.join(os.path.dirname(gridpoint_file),".."))
    expname = os.path.basename(gpfile)[5:9]
    inigpfile,inishfile = None,None
    prevgpfiles,prevshfiles = [],[]
    for f in cmor_utils.find_ifs_output(ifsoutputdir,exp = expname):
        if(f.endswith("+000000")):
            if(os.path.basename(f).startswith("ICMGG")): inigpfile = f
            if(os.path.basename(f).startswith("ICMSH")): inishfile = f
        elif(cmor_utils.get_ifs_date(f) == prevdate):
            if(os.path.basename(f).startswith("ICMGG")): prevgpfiles.append(f)
            if(os.path.basename(f).startswith("ICMSH")): prevshfiles.append(f)
    if(not any(prevgpfiles) or not any(prevshfiles)):
        log.info("No regular previous month files found, taking initial state files...")
        if(not inigpfile):
            log.error("No initial gridpoint file found in %s" % ifsoutputdir)
        if(not inishfile):
            log.error("No initial spectral file found in %s" % ifsoutputdir)
        return inigpfile,inishfile
    if(len(prevgpfiles) > 1):
        log.warning("Multiple previous month gridpoint files found: %s. Taking first match" % ",".join(prevgpfiles))
    if(len(prevshfiles) > 1):
        log.warning("Multiple previous month spectral files found: %s. Taking first match" % ",".join(prevshfiles))
    return prevgpfiles[0],prevshfiles[0]


def execute(tasks):
    return True
