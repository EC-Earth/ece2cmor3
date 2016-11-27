import cdo
import cmor_source

class cdo_command:

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

    grid_operators = [spectral_operator,regrid_operator]
    stat_operators = [minimum_operator,maximum_operator,mean_operator]
    frequencies = [frequency_hr,frequency_3hr,frequency_6hr,frequency_day,frequency_mon,frequency_yr]

    def __init__(self):
        self.source_grid = cmor_source.ifs_grid.point
        self.expr_operators = []
        self.selection_codes = []
        self.time_operators = {}

    def create_command(self):
        sels = cdo_command.selcode_commands(self.selection_codes)
        exps = cdo_command.expression_commands(self.expr_operators)
        tims = cdo_command.time_commands(self.time_operators).sort(lambda (f,o):-cdo_command.frequencies.index(f))
        grds = []
        if(self.source_grid == cmor_source.ifs_grid.point):
            grds.append((cdo_command.gridtype_operator,cdo_command.regular_grid_type))
        elif(self.source_grid == cmor_source.ifs_grid.spec):
            grds.append((cdo_command.spectral_operator,None))
        comm = optimize_order(tims + exps + grds + sels)



    def apply(self,input_file,output_file = None):
        raise Exception("Not implemented")

    @staticmethod
    def selcode_commands(codes):
        if(len(codes)==0): return []
        return [(cdo_command.select_operator,",".join([str(i) for i in set([c.var_id for c in codes])))]

    @staticmethod
    def expression_commands(exprs):
        return [(cdo_command.expr_operator,"'" + e + "'") for e in exprs]

    @staticmethod
    def time_commands(timops):
        return [(k + v,None) for k,v in timops.iteritems()]

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

    @staticmethod
    def linear_operator(operator,argument):
        return operator.endswith["mean"] and operator[:-4] in cdo_command.frequencies
