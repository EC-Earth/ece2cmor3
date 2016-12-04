import logging
import cdoapi
import cmor_source
import cmor_target


# Creates a cdo postprocessing command for the given IFS task.
def create_command(task):
    if(not isinstance(cmor_source.ifs_source,task.source)):
        raise Exception("This function can only be used to create cdo commands for IFS tasks")
    result = cdo_command(code = task.source.get_grib_code().var_id)
    if(task.source.grid() == cmor_source.ifs_grid.spec):
        result.add_operator(cdoapi.spectral_operator)
    else:
        result.add_operator(cdoapi.gridtype_operator,cdoapi.regular_grid_type)
    expr = task.source.getattr(cmor_source.expression_key,None)
    if(expr):
        result.add_operator(cdoapi.expression_operator,expr)
    freq = task.target.frequency
    timops = getattr(task.target,"time_operator",["point"])
    add_time_operators(result,freq,timops)
    add_level_operators(result,task)
    return result


# Translates the cmor time post-processing operation to a cdo command-line option
def add_time_operators(cdo,freq,operators):
    if(freq == "mon"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
            cdo.add_operator(cdoapi.cdo_command.select_day_operator,15)
            return
        if(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            return
        if(operator == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.month])
            return
        if(operator == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.month])
            return
        if(operator == ["maximum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            return
        if(operator == ["minimum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            return
    if(freq == "day"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
            return
        if(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
            return
        if(operator == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            return
        if(operator == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            return
    if(freq == "6hr"):
        if(operators == ["point"] or operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,0,6,12,18)
            return
    if(freq in ["1hr","3hr"]):
        if(operators == ["point"] or operators == ["mean"]): return
    raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")


# Translates the cmor vertical level post-processing operation to a cdo command-line option
def get_cdo_level_commands(cdo,task):
    axisname = getattr(task,"z_axis",None)
    if not axisname:
        return
    if(axisname == "alevel"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.modellevel)
    if(axisname == "alevhalf"):
        log.error("Vertical half-levels in table %s are not supported by this post-processing software",(task.target.table))
        return
    axisinfos = cmor_target.axes.get(task.target.table,{})
    axisinfo = axisinfos.get(axisname,None)
    if(not axisinfo):
        log.error("Could not retrieve information for axis %s in table %s" % (axisname,task.target.table))
        return
    oname = axisinfo.get("standard_name",None)
    if(oname == "air_pressure"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
    elif(oname == "height"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.height)
    else:
        log.error("Could not convert vertical axis type %s to CDO axis selection operator" % oname)
        return
    zlevs = axisinfo.get("requested",[])
    if(len(zlevs) == 0):
        val = axisinfo.get("value",None)
        if(val): zlevs = [val]
    if(len(zlevs) == 1 and task.source.spatial_dims == 2):
        return
    if(len(zlevs) > 1):
        cdo.add_operator(cdoapi.cdo_command.select_lev_operator,zlevs)
