import datetime
import math

import cdo
import cmor
import dateutil.relativedelta
# lpjg related
import gzip
import io
import csv
# lpjg end

import logging
import numpy
import os
import re

# Log object
log = logging.getLogger(__name__)


# Enum utility class
class cmor_enum(tuple): __getattr__ = tuple.index


# Grouping to dictionary utility function
def group(objects, func):
    d = {}
    for o in objects:
        k = func(o)
        if k in d:
            d[k].append(o)
        else:
            d[k] = [o]
    return d


# Turns a date or datetime into a datetime
def make_datetime(time):
    if isinstance(time, datetime.date):
        return datetime.datetime.combine(time, datetime.datetime.min.time())
    elif isinstance(time, datetime.datetime):
        return time
    else:
        raise Exception("Cannot convert object", time, "to datetime")


# Creates a time interval from the input string, assuming ec-earth conventions
def make_cmor_frequency(s):
    if isinstance(s, dateutil.relativedelta.relativedelta) or isinstance(s, datetime.timedelta):
        return s
    if isinstance(s, basestring):
        if s in ["yr", "yrPt", "dec"]:
            return dateutil.relativedelta.relativedelta(years=1)
        if s in ["mon", "monC", "monPt"]:
            return dateutil.relativedelta.relativedelta(months=1)
        if s in ["day", "dayPt"]:
            return dateutil.relativedelta.relativedelta(days=1)
        if s in ["6hr", "6hrPt"]:
            return dateutil.relativedelta.relativedelta(hours=6)
        if s in ["3hr", "3hrPt"]:
            return dateutil.relativedelta.relativedelta(hours=3)
    raise Exception("Could not convert argument", s, "to a relative time interval")


# Creates a time interval from the input string, assuming ec-earth conventions
def get_rounded_time(freq, time, offset=0):
    interval = make_cmor_frequency(freq)
    if interval == dateutil.relativedelta.relativedelta(days=1):
        return datetime.datetime(year=time.year, month=time.month, day=time.day) + offset * interval
    if interval == dateutil.relativedelta.relativedelta(months=1):
        return datetime.datetime(year=time.year, month=time.month, day=1) + offset * interval
    if interval == dateutil.relativedelta.relativedelta(years=1):
        return datetime.datetime(year=time.year, month=1, day=1) + offset * interval
    n = int(offset) if offset > 0 else int(offset) - 1
    delta = ((time + n * interval) - time) / 2
    return time + delta


# Creates time intervals between start and end with length delta. Last interval may be cut to match end-date.
def make_time_intervals(start, end, delta):
    global log
    if end < start:
        log.warning("Start date %s later than end date %s" % (str(start), str(end)))
        return []
    if start + delta == start:
        log.warning("Cannot partition time interval into zero-length intervals")
        return []
    result = list()
    istart = start
    while (istart + delta) < end:
        iend = istart + delta
        result.append((istart, iend))
        istart = iend
    result.append((istart, end))
    return result


# Finds all ifs output in the given directory. If expname is given, matches according output files.
def find_ifs_output(path, expname=None):
    subexpr = ".*"
    if expname:
        subexpr = expname
    expr = re.compile("^(ICMGG|ICMSH)" + subexpr + "\+[0-9]{6}$")
    result = []
    for root, dirs, files in os.walk(path):
        result.extend([os.path.join(root, f) for f in files if re.match(expr, f)])
    return result


# Returns the start date for the given file path
def get_ifs_date(filepath):
    global log
    fname = os.path.basename(filepath)
    regex = re.search("\+[0-9]{6}", fname)
    if not regex:
        log.error("Unable to parse time stamp from ifs file name %s" % fname)
        return None
    ss = regex.group()[1:]
    # prevent runtimeerror for "000000"
    #    return datetime.datetime.strptime("000101","%Y%m").date() if ss.startswith("000000") else datetime.datetime.strptime(ss,"%Y%m").date()
    return datetime.datetime.strptime(ss, "%Y%m").date()


# Finds all nemo output in the given directory. If expname is given, matches according output files.
def find_nemo_output(path, expname=None):
    subexpr = ".*"
    if expname:
        subexpr = expname
    expr = re.compile(subexpr + "_.*_[0-9]{8}_[0-9]{8}_.*.nc$")
    return [os.path.join(path, f) for f in os.listdir(path) if re.match(expr, f)]


# Returns the start and end date corresponding to the given nemo output file.
def get_nemo_interval(filepath):
    global log
    fname = os.path.basename(filepath)
    regex = re.findall("_[0-9]{8}", fname)
    if not regex or len(regex) != 2:
        log.error("Unable to parse dates from nemo file name %s" % fname)
        return None
    start = datetime.datetime.strptime(regex[0][1:], "%Y%m%d")
    end = datetime.datetime.strptime(regex[1][1:], "%Y%m%d")
    return start, end


# Returns the frequency string for a given nemo output file.
def get_nemo_frequency(filepath, expname):
    global log
    f = os.path.basename(filepath)
    expr = re.compile("^" + expname + ".*_[0-9]{8}_[0-9]{8}_.*.nc$")
    if not re.match(expr, f):
        log.error("File path %s does not correspond to nemo output of experiment %s" % (filepath, expname))
        return None
    fstr = f[len(expname) + 1:].split("_")[0]
    expr = re.compile("^(\d+)([hdmy])")
    if not re.match(expr, fstr):
        log.error("File path %s does not contain a valid frequency indicator" % filepath)
        return None
    n = int(fstr[0:len(fstr) - 1])
    if n == 0:
        log.error("Invalid frequency 0 parsed from file path %s" % filepath)
        return None
    return fstr


# Returns the grid for the given file name.
def get_nemo_grid(filepath, expname):
    global log
    f = os.path.basename(filepath)
    expr = re.compile("(?<=^" + expname + "_.{2}_[0-9]{8}_[0-9]{8}_).*.nc$")
    result = re.search(expr, f)
    if not result:
        log.error("File path %s does not contain a grid string" % filepath)
        return None
    match = result.group(0)
    return match[0:len(match) - 3]


def read_time_stamps(path):
    command = cdo.Cdo()
    times = command.showtimestamp(input=path)[0].split()
    return map(lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S"), times)


def find_tm5_output(path, expname=None,varname=None,freq=None):
    subexpr = ".*"
    if expname:
        subexpr = expname
    expr = re.compile(".*_" + subexpr + "_.*_[0-9]{6,12}-[0-9]{6,12}.nc$")

    a=[os.path.join(path, f) for f in os.listdir(path) if re.match(expr, f)]
   
    return [os.path.join(path, f) for f in os.listdir(path) if re.match(expr, f)]

def get_tm5_frequency(filepath, expname):
    global log
    f = os.path.basename(filepath)
    expr = re.compile(".*_[0-9]{6,12}-[0-9]{6,12}.nc$")
    if not re.match(expr, f):
        log.error("File path %s does not correspond to tm5 output of experiment %s" % (filepath, expname))
        return None

    fstr = f.split("_")[1]
    expr = re.compile("(AERhr|AERmon|AERday|fx|Ahr|Amon|Aday|Emon|Efx)")
    #expr = re.compile("(AERhr|AERmon|AERday|Emon|Efx)")
    if not re.match(expr, fstr):
        log.error("File path %s does not contain a valid frequency indicator" % filepath)
        return None
    #n = int(fstr[0:len(fstr))
    #if n == 0:
    #    log.error("Invalid frequency 0 parsed from file path %s" % filepath)
    #    return None
    return fstr
# Returns the start and end date corresponding to the given nemo output file.
def get_tm5_interval(filepath):
    global log
    fname = os.path.basename(filepath)
    regex = re.findall("[0-9]{6,12}", fname) #mon(6),day(8), hour(10)
    if not regex or len(regex) != 2:
        log.error("Unable to parse dates from tm5 file name %s" % fname)
        return None
    if len(regex[0])==8:
        start = datetime.datetime.strptime(regex[0][:], "%Y%m%d")
        end = datetime.datetime.strptime(regex[1][:], "%Y%m%d")
    elif  len(regex[0])==6:
        start = datetime.datetime.strptime(regex[0][:], "%Y%m")
        end = datetime.datetime.strptime(regex[1][:], "%Y%m")
    elif  len(regex[0])==10:
        start = datetime.datetime.strptime(regex[0][:], "%Y%m%d%H")
        end = datetime.datetime.strptime(regex[1][:], "%Y%m%d%H")
    elif  len(regex[0])==12:
        start = datetime.datetime.strptime(regex[0][:], "%Y%m%d%H%M")
        end = datetime.datetime.strptime(regex[1][:], '%Y%m%d%H%M')
    else:
        log.error("Date string in filename %s not supported." % fname)
    
    return start, end


# Writes the ncvar (numpy array or netcdf variable) to CMOR variable with id varid
def netcdf2cmor(varid, ncvar, timdim=0, factor=1.0, term=0.0, psvarid=None, ncpsvar=None, swaplatlon=False,
                fliplat=False, mask=None, missval=1.e+20, time_selection=None):
    global log
    ndims = len(ncvar.shape)
    if timdim < 0:
        ntimes = 1 if time_selection is None else len(time_selection)
    else:
        ntimes = ncvar.shape[timdim] if time_selection is None else len(time_selection)
    size = ncvar.size / ntimes
    chunk = int(math.floor(4.0E+9 / (8 * size)))  # Use max 4 GB of memory
    if time_selection is not None and numpy.any(time_selection < 0):
        chunk = 1
    missval_in = float(getattr(ncvar, "missing_value", missval))
    for i in range(0, ntimes, chunk):
        imax = min(i + chunk, ntimes)
        time_slice = slice(i, imax, 1)
        if time_selection is not None:
            if numpy.array_equal(time_selection[i: imax], numpy.arange(i, imax)):
                time_slice = slice(i, imax, 1)
            elif numpy.array_equal(time_selection[i: imax], numpy.array([-1])):
                time_slice = None
            else:
                time_slice = time_selection[i: imax]
        vals = None
        if ndims == 1:
            if timdim < 0:
                vals = factor * ncvar[:] + term
            elif timdim == 0:
                vals = factor * ncvar[i:imax] + term
        elif ndims == 2:
            if timdim < 0:
                vals = (
                    apply_mask(factor * ncvar[:, :] + term, mask, missval_in, missval)).transpose() if swaplatlon else \
                    apply_mask(factor * ncvar[:, :] + term, mask, missval_in, missval)
            elif timdim == 0:
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[1:], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[time_slice, :] + term, None, missval_in, missval),
                                           axes=[1, 0])
            elif timdim == 1:
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[:-1], missval)
                else:
                    vals = apply_mask(factor * ncvar[:, time_slice] + term, None, missval_in, missval)
        elif ndims == 3:
            if timdim < 0:
                vals = numpy.transpose(apply_mask(factor * ncvar[:, :, :] + term, mask, missval_in, missval),
                                       axes=[2, 1, 0] if swaplatlon else [1, 2, 0])
            elif timdim == 0:
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[1:], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[time_slice, :, :] + term, mask,
                                                      missval_in, missval),
                                           axes=[2, 1, 0] if swaplatlon else [1, 2, 0])
            elif timdim == 2:
                if mask is not None:
                    log.error("Masking column-major stored arrays is not implemented yet...ignoring mask")
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[:-1], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[:, :, time_slice] + term, None, missval_in,
                                                      missval),
                                           axes=[1, 0, 2] if swaplatlon else [0, 1, 2])
            else:
                log.error("Unsupported array structure with 3 dimensions and time dimension index 1")
                return
        elif ndims == 4:
            if timdim == 0:
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[1:], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[time_slice, :, :, :] + term, mask, missval_in,
                                                      missval),
                                           axes=[3, 2, 1, 0] if swaplatlon else [2, 3, 1, 0])
            elif timdim == 3:
                if mask is not None:
                    log.error("Masking column-major stored arrays is not implemented yet...ignoring mask")
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[:-1], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[:, :, :, time_slice] + term, mask, missval_in,
                                                      missval),
                                           axes=[1, 0, 2, 3] if swaplatlon else [0, 1, 2, 3])
            else:
                log.error("Unsupported array structure with 4 dimensions and time dimension index %d" % timdim)
                return
        elif ndims == 5:
            if timdim == 0:
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[1:], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[time_slice, :, :, :, :] + term, mask, missval_in,
                                                      missval),
                                           axes=[4, 3, 2, 1, 0] if swaplatlon else [3, 4, 2, 1, 0])
            elif timdim == 4:
                if mask is not None:
                    log.error("Masking column-major stored arrays is not implemented yet...ignoring mask")
                if time_slice is None:
                    vals = numpy.full(ncvar.shape[:-1], missval)
                else:
                    vals = numpy.transpose(apply_mask(factor * ncvar[:, :, :, :, time_slice] + term, mask, missval_in,
                                                      missval),
                                           axes=[1, 0, 2, 3, 4] if swaplatlon else [0, 1, 2, 3, 4])
            else:
                log.error("Unsupported array structure with 4 dimensions and time dimension index %d" % timdim)
                return
        else:
            log.error("Cmorizing arrays of rank %d is not supported" % ndims)
            return
        if fliplat and (ndims > 1 or timdim < 0):
            vals = numpy.flipud(vals)
        if timdim < 0 and ntimes > 1:
            vals = numpy.repeat(vals, repeats=(imax - i), axis=ndims-1)
        cmor.write(varid, vals, ntimes_passed=(0 if (timdim < 0 and ntimes == 1) else (imax - i)))
        del vals
        if psvarid is not None and ncpsvar is not None:
            spvals = None
            if len(ncpsvar.shape) == 3:
                spvals = numpy.transpose(ncpsvar[i:imax, :, :], axes=[2, 1, 0] if swaplatlon else [1, 2, 0])
            elif len(ncpsvar.shape) == 4:
                projvar = ncpsvar[i:imax, 0, :, :]
                spvals = numpy.transpose(projvar, axes=[2, 1, 0] if swaplatlon else [1, 2, 0])
            if spvals is not None:
                if fliplat:
                    spvals = numpy.flipud(spvals)
                cmor.write(psvarid, spvals, ntimes_passed=(0 if timdim < 0 else (imax - i)), store_with=varid)
                del spvals


# Applies the mask to the 2 trailing dimensions of the input array, or else replaces the missing values.
def apply_mask(array, mask, missval_in, missval_out):
    if mask is not None:
        numpy.putmask(array, numpy.broadcast_to(numpy.logical_not(mask), array.shape), missval_out)
    elif missval_in != missval_out:
        array[array == missval_in] = missval_out
    return array
