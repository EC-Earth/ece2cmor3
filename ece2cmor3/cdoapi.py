import thread
import numpy
import logging
import cdo
import os

# Log object
log = logging.getLogger(__name__)


# Class for interfacing with the CDO python wrapper.
class cdo_command:
    # CDO operator strings
    timselmean_operator = "timselmean"
    timselmin_operator = "timselmin"
    timselmax_operator = "timselmax"
    select_code_operator = "selcode"
    select_var_operator = "selvar"
    set_code_operator = "setcode"
    expression_operator = "expr"
    add_expression_operator = "aexpr"
    spectral_operator = "sp2gpl"
    gridtype_operator = "setgridtype"
    select_z_operator = "selzaxis"
    select_lev_operator = "sellevel"
    min_time_operators = {"day": "daymin", "mon": "monmin", "year": "yearmin"}
    max_time_operators = {"day": "daymax", "mon": "monmax", "year": "yearmin"}
    mean_time_operators = {"day": "daymean", "mon": "monmean", "year": "yearmean"}
    sum_time_operators = {"day": "daysum", "mon": "monsum", "year": "yearsum"}
    select_hour_operator = "selhour"
    select_day_operator = "selday"
    select_month_operator = "selmon"
    select_step_operator = "seltimestep"
    shift_time_operator = "shifttime"
    ml2pl_operator = "ml2plx"
    ml2hl_operator = "ml2hl"
    merge_operator = "merge"

    # CDO operator argument strings
    regular_grid_type = "regular"
    hour = "hr"
    day = "day"
    month = "mon"
    year = "year"
    height = "height"
    pressure = "pressure"
    model_level = "hybrid"
    surf_level = "surface"

    # Optimized operator ordering for CDO:
    operator_ordering = [set_code_operator, mean_time_operators[year], min_time_operators[year],
                         max_time_operators[year], mean_time_operators[month], min_time_operators[month],
                         max_time_operators[month], mean_time_operators[day], min_time_operators[day],
                         max_time_operators[day], timselmean_operator, gridtype_operator, ml2pl_operator,
                         ml2hl_operator, add_expression_operator, expression_operator, spectral_operator,
                         select_lev_operator, select_z_operator, select_hour_operator, select_day_operator,
                         select_month_operator, shift_time_operator, select_step_operator, select_code_operator]

    # Constructor
    def __init__(self, code=0):
        self.operators = {}
        self.app = cdo.Cdo()
        if code > 0:
            self.add_operator(cdo_command.select_code_operator, code)

    # Adds an operator
    def add_operator(self, operator, *args):
        global log
        if operator in cdo_command.operator_ordering:
            added_args = ["'" + a + "'" for a in args] if operator == cdo_command.expression_operator else list(args)
            if operator not in self.operators:
                self.operators[operator] = added_args
            else:
                self.operators[operator].extend(added_args)
        else:
            log.error("Unknown operator was rejected: ", operator)

    # Creates a command string from the given operator list
    def create_command(self):
        keys = cdo_command.optimize_order(
            sorted(self.operators.keys(), key=lambda op: cdo_command.operator_ordering.index(op)))
        return " ".join([cdo_command.make_option(k, self.operators[k]) for k in keys])

    def merge(self, ifiles, ofile):
        if isinstance(ifiles, str):
            return self.app.merge(input=ifiles, output=ofile)
        return self.app.merge(input=' '.join(ifiles), output=ofile)

    def show_code(self, ifile):
        return self.app.showcode(input=ifile)

    # Applies the current set of operators to the input file.
    def apply(self, ifile, ofile=None, threads=4, grib_first=False):
        global log
        keys = cdo_command.optimize_order(
            sorted(self.operators.keys(), key=lambda op: cdo_command.operator_ordering.index(op)))
        option_string = "-f nc" if threads < 2 else ("-f nc -P " + str(threads))
        if grib_first:
            option_string = "" if threads < 2 else ("-P " + str(threads))
        func = getattr(self.app, keys[0], None)
        app_args = None
        if func:
            app_args = ",".join([str(a) for a in self.operators.get(keys[0], [])])
            input_string = " ".join([cdo_command.make_option(k, self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(self.app, "copy")
            input_string = " ".join([cdo_command.make_option(k, self.operators[k]) for k in keys] + [ifile])
        output_file = ofile
        if ofile and grib_first:
            output_file = ofile[:-3] + ".grib"
        try:
            if app_args and ofile:
                f = func(app_args, input=input_string, output=output_file, options=option_string)
            elif app_args:
                f = func(app_args, input=input_string, options=option_string)
            elif ofile:
                f = func(input=input_string, output=output_file, options=option_string)
            else:
                f = func(input=input_string, options=option_string)
            if grib_first:
                option_string = "-f nc"
                self.app.copy(input=output_file, output=ofile, options=option_string)
                os.remove(output_file)
        except cdo.CDOException as e:
            log.error(str(e))
            return None
        return f

    # Applies the current set of operators and returns the netcdf variables in memory:
    def apply_cdf(self, ifile, threads=4):
        keys = cdo_command.optimize_order(
            sorted(self.operators.keys(), key=lambda op: cdo_command.operator_ordering.index(op)))
        option_string = "" if threads < 2 else ("-P " + str(threads))
        func = getattr(self.app, keys[0], None)
        app_args = None
        if func:
            app_args = ",".join([str(a) for a in self.operators.get(keys[0], [])])
            input_string = " ".join([cdo_command.make_option(k, self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(self.app, "copy")
            input_string = " ".join([cdo_command.make_option(k, self.operators[k]) for k in keys] + [ifile])
        try:
            if app_args:
                return func(app_args, input=input_string, options=option_string, returnCdf=True).variables
            else:
                return func(input=input_string, options=option_string, returnCdf=True).variables
        except cdo.CDOException as e:
            log.error(str(e))
            return None

    # Grid description method
    def get_grid_descr(self, ifile):
        global log
        int_fields = ["gridsize", "np", "xsize", "ysize"]
        real_fields = ["xfirst", "xinc", "yfirst", "yinc"]
        array_fields = ["xvals", "yvals"]
        infolist = []
        try:
            infolist = self.app.griddes(input=ifile)
        except cdo.CDOException as e:
            log.error(str(e))
        info_dict = {}
        prev_key = ""
        for info in infolist:
            s = str(info)
            if len(s) == 0:
                continue
            if s[0] == '#':
                continue
            string_list = s.split('=')
            if len(string_list) == 0:
                continue
            elif len(string_list) == 1:
                if prev_key in info_dict:
                    info_dict[prev_key] += (' ' + string_list[0].strip())
                else:
                    log.error("Could not connect grid description line %s to an "
                              "existing key-value pair" % string_list[0])
                    continue
            elif len(string_list) == 2:
                key = string_list[0].strip()
                info_dict[key] = string_list[1].strip()
                prev_key = key
            else:
                log.error("Could not parse grid description line %s as a key-value pair" % s)
                continue
        for k, v in info_dict.iteritems():
            if k in int_fields:
                info_dict[k] = int(v)
            if k in real_fields:
                info_dict[k] = float(v)
            if k in array_fields:
                info_dict[k] = numpy.array([float(x) for x in v.split()])
        return info_dict

    # Returns a list vertical axes corresponding to the input variable
    def get_z_axes(self, ifile, var):
        if not ifile:
            return []
        select_operator = cdo_command.select_code_operator if isinstance(var, int) else cdo_command.select_var_operator
        try:
            output = self.app.showltype(input=" ".join([cdo_command.make_option(select_operator, [var]), ifile]))
        except cdo.CDOException as e:
            log.error(str(e))
            return []
        if isinstance(output, list):
            output = output[0]
        return [] if not output else [int(s) for s in output.split()]

    # Returns a list of levels for a given variable and axis
    def get_levels(self, ifile, var, axis):
        if not ifile:
            return []
        select_operator = cdo_command.select_code_operator if isinstance(var, int) else cdo_command.select_var_operator
        selvar_operator = cdo_command.make_option(select_operator, [var])
        selzaxis_operator = cdo_command.make_option(cdo_command.select_z_operator, [axis])
        try:
            output = self.app.showlevel(input=" ".join([selzaxis_operator, selvar_operator, ifile]))
        except cdo.CDOException as e:
            log.error(str(e))
            return []
        if isinstance(output, list):
            output = output[0]
        return [] if not output else [float(s) for s in output.split()]

    # Option writing utility function
    @staticmethod
    def make_option(key, args):
        option = "-" + key
        if key == cdo_command.add_expression_operator and len(args) > 1:
            return option + ",\'" + ';'.join([str(a) for a in args]) + "\'"
        return (option + "," + ",".join([str(a) for a in args])) if any(args) else option

    # Reshuffles operator ordering to increase performance
    @staticmethod
    def optimize_order(operator_list):
        i1 = operator_list.index(cdo_command.spectral_operator) if cdo_command.spectral_operator in operator_list else 0
        i2 = operator_list.index(cdo_command.gridtype_operator) if cdo_command.gridtype_operator in operator_list else 0
        nonlinear_operators = cdo_command.min_time_operators.values() + cdo_command.max_time_operators.values() + [
            cdo_command.expression_operator, cdo_command.add_expression_operator]
        i = i1 + i2
        while i > 0:
            if operator_list[i - 1] in nonlinear_operators:
                break
            operator_list[i - 1], operator_list[i] = operator_list[i], operator_list[i - 1]
            i -= 1
        return operator_list
