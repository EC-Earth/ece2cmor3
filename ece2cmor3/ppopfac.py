import logging
import re

from dateutil.relativedelta import relativedelta
from ece2cmor3 import ppsh, pptime, pplevels, pp2cmor, ppexpr, cmor_target, grib_file, cmor_source

# Log object
log = logging.getLogger(__name__)

# Masks, assigned by ifs2cmor
masks = {}

# CMOR table root assigned by ifs2cmor
table_root = None


# Creates the DAG of post-processing operators for a specific task

def create_pp_operators(task):
    pp2cmor.table_root = table_root
    expr = None
    if task.source.get_root_codes() != [task.source.get_grib_code()]:
        expr = getattr(task.source, cmor_source.expression_key, None)

    expr_operator = create_expr_operator(expr)
    time_operator = create_time_operator(task)
    zaxis_operator = create_level_operator(task)
    cmor_operator = create_cmor_operator(task)

    if time_operator is None:
        log.warning("Dismissing task without time operator: %s in %s" % (task.target.variable, task.target.table))
        return None

    operators = [zaxis_operator, expr_operator, time_operator, cmor_operator]
    operator_chain = [o for o in operators if o is not None]

    for i in range(0, len(operator_chain) - 1):
        operator_chain[i].targets.append(operator_chain[i + 1])
    return operator_chain[0]


def create_cmor_operator(task):
    axisname, leveltype, levs = cmor_target.get_z_axis(task.target)
    store_var_key = (134, 128, grib_file.surface_level_code, 0) if leveltype in ["alevel", "alevhalf"] else None
    mask_key, mask_expr = None, None
    if not hasattr(task, cmor_target.mask_key):
        for area_operator in getattr(task.target, "area_operator", []):
            words = area_operator.split()
            if len(words) == 3 and words[1] == "where":
                setattr(task.target, cmor_target.mask_key, words[2])
    mask = getattr(task.target, cmor_target.mask_key, None)
    if mask:
        if mask not in masks:
            log.warning("Mask %s is not supported as an IFS mask, skipping masking" % mask)
            delattr(task.target, cmor_target.mask_key)
        else:
            mask_expr = masks[mask]
            varstrs = re.findall("var[0-9]{1,3}", mask_expr)
            if len(varstrs) != 1:
                log.error("Cannot parse mask expression %s to single variable expression" % mask_expr)
            else:
                mask_code = cmor_source.grib_code.read(varstrs[0])
                mask_key = (mask_code.var_id, mask_code.tab_id, grib_file.surface_level_code, 0)
    cmor_operator = pp2cmor.msg_to_cmor(task, store_var_key, mask_key)
    if mask_key is not None:
        cmor_operator.mask_expression = mask_expr
    return cmor_operator


def create_expr_operator(expr):
    return None if expr is None else ppexpr.variable_expression(expr)


# Creates a time selection/aggregation operator for a specific task
def create_time_operator(task):
    freq = getattr(task.target, cmor_target.freq_key, None)
    operators = getattr(task.target, "time_operator", ["point"])
    periods = {"mon": relativedelta(months=1), "day": relativedelta(days=1)}
    operator_dict = {"mean": pptime.time_aggregator.linear_mean_operator,
                     "minimum": pptime.time_aggregator.min_operator,
                     "maximum": pptime.time_aggregator.max_operator}
    if len(operators) == 2 and operators[1] == "mean over years" and operators[0].endswith("within years"):
        clim_operator = operators[0][:-13]
        operators = [clim_operator]
    if len(operators) == 1:
        period, operator = periods.get(freq, None), operator_dict.get(operators[0], None)
        if period is None:
            # TODO: catch subhrPt
            if freq.endswith("hr"):
                period = relativedelta(hours=int(freq[:-2]))
            if freq.endswith("hrPt"):
                period = relativedelta(hours=int(freq[:-4]))
        if operators == ["point"]:
            if freq.endswith("hrPt"):
                return pptime.time_filter(period, time_bounds=False)
            elif freq.endswith("hr"):
                log.warning("Time operator point for variable %s in table %s without hrPt-frequency... "
                            "still using point sampling" % (task.target.variable, task.target.table))
                return pptime.time_filter(period, time_bounds=False)
        if operators == ["mean"] and freq.endswith("hr"):
            if all([c in cmor_source.ifs_source.grib_codes_accum for c in task.source.get_root_codes()]):
                return pptime.time_filter(period, time_bounds=True)
            else:
                log.warning("Requesting average over %d hours for instantaneous field %s is not supported, switching "
                            "to time sampling" % (period.hours, str(task.source.get_grib_code())))
            return pptime.time_filter(period, time_bounds=True)
        if period is not None and operator is not None:
            return pptime.time_aggregator(operator, period)
    log.error("Unsupported combination of frequency %s with time operators %s encountered for %s in table %s" %
              (freq, str(operators), task.target.variable, task.target.table))
    task.set_failed()
    return None


# Creates a vertical level aggregation operator for a specific task
def create_level_operator(task):
    # TODO Correct this for composed variables
    if task.source.get_grib_code() not in cmor_source.ifs_source.grib_codes_3D:
        return None
    axisname, leveltype, levels = cmor_target.get_z_axis(task.target)
    if leveltype == "alevel":
        return pplevels.level_aggregator(level_type=grib_file.hybrid_level_code, levels=None)
    if leveltype == "alevhalf":
        log.error("Vertical half-levels in table %s are not supported by this post-processing software",
                  task.target.table)
        task.set_failed()
        return None
    if leveltype in ["height", "altitude"]:
        return pplevels.level_aggregator(level_type=grib_file.height_level_code, levels=[float(l) for l in levels])
    if leveltype in ["air_pressure"]:
        return pplevels.level_aggregator(level_type=grib_file.pressure_level_code, levels=[float(l) for l in levels])
    return None
