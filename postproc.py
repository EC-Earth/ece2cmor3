import logging
import cdoapi
import cmor_target

# Creates a cdo postprocessing command for the given IFS task.
def create_command(task):
    if(not isinstance(cmor_source.ifs_source,task.source)):
        raise Exception("This function can only be used to create cdo commands for IFS tasks")
    result = cdo_command()
    expr = task.source.getattr(cmor_source.expression_key,None)
    if(expr):
        result.expr_operators = [expr]
        result.selection_codes.extend(task.source.get_root_codes())
    else:
        result.selection_codes = [task.source.get_grib_code()]
    freq = task.target.frequency
    timops = getattr(task.target,"time_operator",["point"])
    result.time_operators = convert_time_operators(freq,timops)
    return result


# Translates the cmor time post-processing operation to a cdo command-line option
def convert_time_operators(freq,operators):
    if(freq == "mon"):
        if(operators == ["point"]): return ["selhour,12","selday,15"]
        if(operators == ["mean"]): return ["monmean"]
        if(operator == ["maximum"]): return ["monmax"]
        if(operator == ["minimum"]): return ["monmin"]
        if(operator == ["maximum within days","mean over days"]): return ["monmean","daymax"]
        if(operator == ["minimum within days","mean over days"]): return ["monmean","daymin"]
    if(freq == "day"):
        if(operators == ["point"]): return ["selhour,12"]
        if(operators == ["mean"]): return ["daymean"]
        if(operator == ["maximum"]): return ["daymax"]
        if(operator == ["minimum"]): return ["daymin"]
    if(freq == "6hr"):
        if(operators == ["point"] or operators == ["mean"]): return ["selhour,0,6,12,18"]
    if(freq in ["1hr","3hr"]):
        if(operators == ["point"] or operators == ["mean"]): return []
    raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")


# Translates the cmor vertical level post-processing operation to a cdo command-line option
def get_cdo_level_commands(task):
    axisname = getattr(task,"z_axis",None)
    if not axisname:
        return [None,None]
    if(axisname == "alevel"):
        return ["selzaxis,hybrid",None]
    if(axisname == "alevhalf"):
        raise Exception("Half-level fields are not implemented yet")
    axisinfos = cmor_target.axes.get(task.target.table,{})
    axisinfo = axisinfos.get(axisname,None)
    if(not axisinfo):
        log.error("Could not retrieve information for axis %s in table %s" % (axisname,task.target.table))
        return [None,None]
    ret = [None,None]
    oname = axisinfo.get("standard_name",None)
    if(oname == "air_pressure"):
        ret[0] = "selzaxis,pressure"
    elif(oname == "height"):
        ret[0] = "selzaxis,height"
    else:
        log.error("Could not convert vertical axis type %s to CDO axis selection operator" % oname)
        return [None,None]
    zlevs = axisinfo.get("requested",[])
    if(len(zlevs) == 0):
        val = axisinfo.get("value",None)
        if(val): zlevs = [val]
    if(len(zlevs) == 1 and task.source.spatial_dims == 2):
	return (None,None)
    if(len(zlevs) > 1): ret[1] = ",".join(["sellevel"] + zlevs)
    return ret
