import cdo
import cmor_task

class cdo_command:

    def __init__(self):
        self.remap_grid_command = None
        self.expr_operators = []
        self.selection_codes = []
        self.time_operators = []

    def selcode_command(self,code):
        
