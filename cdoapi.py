import thread
import logging
import cdo

# Log object
log = logging.getLogger(__name__)

# CDO instances
cdo_instances = {}

def cleanup():
    for k,v in cdo_instances.iteritems():
        del v
    cdo_instances = {}

# Class for interfacing with the CDO python wrapper.
class cdo_command:

    # CDO operator strings
    select_code_operator  = "selcode"
    expression_operator   = "expr"
    spectral_operator     = "sp2gpl"
    gridtype_operator     = "setgridtype"
    select_z_operator     = "selzaxis"
    select_lev_operator   = "sellevel"
    min_time_operators    = {"day":"daymin","mon":"monmin"}
    max_time_operators    = {"day":"daymax","mon":"monmax"}
    mean_time_operators   = {"day":"daymean","mon":"monmean"}
    select_hour_operator  = "selhour"
    select_day_operator   = "selday"
    select_month_operator = "selmon"
    shift_time_operator   = "shifttime"

    # CDO operator argument strings
    regular_grid_type     = "regular"
    hour                  = "hr"
    day                   = "day"
    month                 = "mon"
    year                  = "year"
    height                = "height"
    pressure              = "pressure"
    modellevel            = "hybrid"

    # Optimized operator ordering for CDO:
    operator_ordering = [mean_time_operators[month],min_time_operators[month],max_time_operators[month],\
                         mean_time_operators[day],min_time_operators[day],max_time_operators[day],\
                         expression_operator,spectral_operator,gridtype_operator,select_lev_operator,select_z_operator,\
                         select_hour_operator,select_day_operator,select_month_operator,shift_time_operator,select_code_operator]

    # Constructor
    def __init__(self,code = 0):
        self.operators = {}
        if(code > 0):
            self.add_operator(cdo_command.select_code_operator,code)

    # Adds an operator
    def add_operator(self,operator,*args):
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

    # Applies the current set of operators to the input file
    def apply(self,ifile,ofile = None,threads = 4):
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        app = cdo_command.get_cdo()
        optionstr = "-f nc" if threads < 2 else ("-f nc -P " + str(threads))
        func = getattr(app,keys[0],None)
        appargs = None
        if(func):
            appargs = ",".join([str(a) for a in self.operators.get(keys[0],[])])
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(app,"copy")
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys] + [ifile])
        f = ofile
        if(appargs and ofile):
            f = func(appargs,input = inputstr,output = ofile,options = optionstr)
        elif(appargs):
            f = func(appargs,input = inputstr,options = optionstr)
        elif(ofile):
            f = func(input = inputstr,output = ofile,options = optionstr)
        else:
            f = func(input = inputstr,options = optionstr)
        return f

    # Applies the current set of operators and returns the netcdf variables in memory:
    def applycdf(self,ifile,threads = 4):
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        app = cdo_command.get_cdo()
        optionstr = "" if threads < 2 else ("-P " + str(threads))
        func = getattr(app,keys[0],None)
        appargs = None
        if(func):
            appargs = ",".join([str(a) for a in self.operators.get(keys[0],[])])
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys[1:]] + [ifile])
        else:
            func = getattr(app,"copy")
            inputstr = " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys] + [ifile])
        if(appargs):
            return func(appargs,input = inputstr,options = optionstr,returnCdf = True).variables
        else:
            return func(input = inputstr,options = optionstr,returnCdf = True).variables

    # Returns the thread-specific cdo instance, or adds it if necessary
    @staticmethod
    def get_cdo():
	global cdo_instances
        threadid = thread.get_ident()
        if(threadid not in cdo_instances):
            cdo_instances[threadid] = cdo.Cdo()
        return cdo_instances[threadid]

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
