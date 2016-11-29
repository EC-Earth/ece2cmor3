import cdo
import cmor_source
import cmor_task

# Class for interfacing with the CDO python wrapper.
class cdo_command:

    # Utility strings
    select_operator = "selcode"
    expr_operator = "aexpr"
    spectral_operator = "sp2gpl"
    gridtype_operator = "setgridtype"
    regular_grid_type = "regular"
    minimum_operator = "min"
    maximum_operator = "max"
    mean_operator = "mean"
    frequency_hr  = "hr"
    frequency_3hr = "3hr"
    frequency_6hr = "6hr"
    frequency_day = "day"
    frequency_mon = "mon"
    frequency_yr = "year"

    # Utility arrays
    grid_operators = [spectral_operator,regrid_operator]
    stat_operators = [minimum_operator,maximum_operator,mean_operator]
    frequencies = [frequency_hr,frequency_3hr,frequency_6hr,frequency_day,frequency_mon,frequency_yr]

    # Constructor
    def __init__(self):
        self.source_grid = cmor_source.ifs_grid.point
        self.expr_operators = []
        self.selection_codes = []
        self.time_operators = {}

    # Creates a command string from the given data
    def create_command(self):
        sels = cdo_command.selcode_commands(list(set(self.selection_codes)))
        exps = cdo_command.expression_commands(list(set(self.expr_operators)))
        tims = cdo_command.time_commands(self.time_operators).sort(lambda (f,o):-cdo_command.frequencies.index(f))
        grds = []
        if(self.source_grid == cmor_source.ifs_grid.point):
            grds.append((cdo_command.gridtype_operator,cdo_command.regular_grid_type))
        elif(self.source_grid == cmor_source.ifs_grid.spec):
            grds.append((cdo_command.spectral_operator,None))
        return " -".join(optimize_order(tims + exps + grds + sels))

    # Attempts to merge the command with the argument command
    def try_join(self,other):
        if(self.source_grid != other.source_grid):
            return False
        if(self.time_operators != other.time_operators):
            return False
        self.expr_operators.expand(other.expr_operators)
        self.selection_codes.expand(other.selection_codes)
        return True

    # Applies the command to the given input, to produce the output file ofile. If not given, the method returns a netcdf array.
    def apply(self,ifile,ofile = None):
        app = cdo.Cdo()
        if(ofile):
            app.copy(input = self.create_command() + " " + ifile,output = ofile,options = "-P 4 -f nc")
            return ofile
        return app.copy(input = self.create_command() + " " + ifile,returnCdf = True).variables

    # Creates a grib code selection command
    @staticmethod
    def selcode_commands(codes):
        if(len(codes)==0): return []
        return [(cdo_command.select_operator,",".join([str(i) for i in set([c.var_id for c in codes])))]

    # Creates a CDO expression command
    @staticmethod
    def expression_commands(exprs):
        return [(cdo_command.expr_operator,"'" + e + "'") for e in exprs]

    # Creates a CDO time averaging command
    @staticmethod
    def time_commands(timops):
        return [(k + v,None) for k,v in timops.iteritems()]

    # Reshuffles operator ordering to increase performance
    @staticmethod
    def optimize_order(oplist):
        i = 0
        for t in oplist:
            if(t[0] in cdo_command.grid_operators):
                break
            else:
                i += 1
        if(i == 0 or i == len(oplist)): return
        while(i > 0 and cdo_command.linear_operator(oplist[i-1][0],oplist[i-1][1])):
            oplist[i-1],oplist[i] = oplist[i],oplist[i-1]

    # Returns whether the time operator may be interchanged with linear operators.
    @staticmethod
    def linear_operator(operator,argument):
        return operator.endswith["mean"] and operator[:-4] in cdo_command.frequencies

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
