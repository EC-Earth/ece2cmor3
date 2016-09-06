from datetime import timedelta

# Class for cmor target objects, which represent output variables.

class cmor_target(object):

    def __init__(self,var_id__,tab_id__):
        self.variable=var_id__
        self.table=tab_id__
        self.frequency=datetime.timedelta(0)
