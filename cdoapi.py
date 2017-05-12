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
    select_code_operator    = "selcode"
    set_code_operator       = "setcode"
    expression_operator     = "expr"
    add_expression_operator = "aexpr"
    spectral_operator       = "sp2gpl"
    gridtype_operator       = "setgridtype"
    select_z_operator       = "selzaxis"
    select_lev_operator     = "sellevel"
    min_time_operators      = {"day":"daymin","mon":"monmin"}
    max_time_operators      = {"day":"daymax","mon":"monmax"}
    mean_time_operators     = {"day":"daymean","mon":"monmean"}
    select_hour_operator    = "selhour"
    select_day_operator     = "selday"
    select_month_operator   = "selmon"
    select_step_operator    = "seltimestep"
    shift_time_operator     = "shifttime"

    # CDO operator argument strings
    regular_grid_type       = "regular"
    hour                    = "hr"
    day                     = "day"
    month                   = "mon"
    year                    = "year"
    height                  = "height"
    pressure                = "pressure"
    modellevel              = "hybrid"

    # Optimized operator ordering for CDO:
    operator_ordering = [set_code_operator,mean_time_operators[month],min_time_operators[month],max_time_operators[month],\
                         mean_time_operators[day],min_time_operators[day],max_time_operators[day],add_expression_operator,\
                         expression_operator,spectral_operator,gridtype_operator,select_lev_operator,select_z_operator,\
                         select_hour_operator,select_day_operator,select_month_operator,shift_time_operator,\
                         select_step_operator,select_code_operator]

    # Constructor
    def __init__(self,code = 0):
        self.operators = {}
        self.app = cdo.Cdo()
        if(code > 0):
            self.add_operator(cdo_command.select_code_operator,code)

    # Adds an operator
    def add_operator(self,operator,*args):
        global log
        if(operator in cdo_command.operator_ordering):
            addedargs = ["'" + a + "'" for a in args] if operator == cdo_command.expression_operator else list(args)
            if(operator not in self.operators):
                self.operators[operator] = addedargs
            else:
                self.operators[operator].extend(addedargs)
        else:
            log.error("Unknown operator was rejected: ",operator)

    # Creates a command string from the given operator list
    def create_command(self):
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        return " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys])

    # Applies the current set of operators to the input file.
    def apply(self,ifile,ofile = None,threads = 4,grib_first = False):
        global log
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        optionstr = "-f nc" if threads < 2 else ("-f nc -P " + str(threads))
        if(grib_first):
            optionstr = "" if threads < 2 else ("-P " + str(threads))
        func = getattr(self.app,keys[0],None)
        appargs = None
        if(func):
            appargs = ",".join([str(a) for a in self.operators.get(keys[0],[])])
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(self.app,"copy")
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys] + [ifile])
        outputfile = ofile[:-3]+".grib" if grib_first else ofile
        f = ofile
        try:
            if(appargs and ofile):
                f = func(appargs,input = inputstr,output = outputfile,options = optionstr)
            elif(appargs):
                f = func(appargs,input = inputstr,options = optionstr)
            elif(ofile):
                f = func(input = inputstr,output = outputfile,options = optionstr)
            else:
                f = func(input = inputstr,options = optionstr)
            if(grib_first):
                optionstr = "-f nc"
                self.app.copy(input = outputfile,output = ofile,options = optionstr)
                os.remove(outputfile)
        except cdo.CDOException as e:
            log.error(str(e))
            return None
        return f

    # Applies the current set of operators and returns the netcdf variables in memory:
    def applycdf(self,ifile,threads = 4):
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        optionstr = "" if threads < 2 else ("-P " + str(threads))
        func = getattr(self.app,keys[0],None)
        appargs = None
        if(func):
            appargs = ",".join([str(a) for a in self.operators.get(keys[0],[])])
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(app,"copy")
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys] + [ifile])
        try:
            if(appargs):
                return func(appargs,input = inputstr,options = optionstr,returnCdf = True).variables
            else:
                return func(input = inputstr,options = optionstr,returnCdf = True).variables
        except cdo.CDOException as e:
            log.error(str(e))
            return None

    # Grid description method
    def get_griddes(self,ifile):
        global log
        intfields = ["gridsize","np","xsize","ysize"]
        realfields = ["xfirst","xinc","yfirst","yinc"]
        arrayfields = ["xvals","yvals"]
        infolist = self.app.griddes(input = ifile)
        infodict = {}
        prevkey = ""
        for info in infolist:
            s = str(info)
            if(len(s) == 0): continue
            if(s[0] == '#'): continue
            slist = s.split('=')
            if(len(slist) == 0):
                continue
            elif(len(slist) == 1):
                if(prevkey in infodict):
                    infodict[prevkey] += (' ' + slist[0].strip())
                else:
                    log.error("Could not connect grid description line %s to an existing key-value pair" % slist[0])
                    continue
            elif(len(slist) == 2):
                key = slist[0].strip()
                infodict[key] = slist[1].strip()
                prevkey = key
            else:
                log.error("Could not parse grid description line %s as a key-value pair" % s)
                continue
        for k,v in infodict.iteritems():
            if(k in intfields): infodict[k] = int(v)
            if(k in realfields): infodict[k] = float(v)
            if(k in arrayfields): infodict[k] = numpy.array([float(x) for x in v.split()])
        return infodict

    # Option writing utility function
    @staticmethod
    def make_option(key,args):
        option = "-" + key
        return (option + "," + ",".join([str(a) for a in args])) if any(args) else option

    # Reshuffles operator ordering to increase performance
    @staticmethod
    def optimize_order(oplist):
        i1 = oplist.index(cdo_command.spectral_operator) if cdo_command.spectral_operator in oplist else 0
        i2 = oplist.index(cdo_command.gridtype_operator) if cdo_command.gridtype_operator in oplist else 0
        nonlinear_operators = cdo_command.min_time_operators.values() + cdo_command.max_time_operators.values() + [cdo_command.expression_operator]
        i = i1 + i2
        while(i > 0):
            if(oplist[i-1] in nonlinear_operators): break
            oplist[i-1],oplist[i] = oplist[i],oplist[i-1]
            i-=1
        return oplist
