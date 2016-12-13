import logging
import cdo

# Log object
log = logging.getLogger(__name__)

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

    # Creates a command string from the given data
    def create_command(self):
        keys = cdo_command.optimize_order(sorted(self.operators.keys(),key = lambda k: cdo_command.operator_ordering.index(k)))
        return " ".join([cdo_command.make_option(k,self.operators[k]) for k in keys])

    # Applies the command to the given input, to produce the output file ofile. If not given, the method returns a netcdf array.
    def apply(self,ifile,ofile = None,threads = 4):
        app = cdo.Cdo()
        threadopstr = "" if threads < 2 else (" -P " + str(threads))
        if(ofile):
            app.copy(input = self.create_command() + " " + ifile,output = ofile,options = "-f nc" + threadopstr)
            return ofile
        return app.copy(input = self.create_command() + " " + ifile,returnCdf = True,options = threadopstr).variables

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
