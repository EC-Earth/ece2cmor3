import os
import cmor

class cmorapi:

    def __init__(self,table_root_,config_file):
        self.table_root = table_root_
        self.current_table = None
        self.tables = {}
        self.grids = {}
        self.time_axes = {}
        self.depth_axes = {}
        cmor.setup(os.path.dirname(table_root_))
        cmor.dataset_json(config_file)

    def load_table(self,table):
        tabid = cmor.load_table(self.table_root + "_" + table + ".json")
        self.tables[tabid] = tabid
        self.current_table = table
        return tabid

    def set_calendar(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)

    def create_axis(self,table,entry,axeslist,createfunc):
        if((table,entry) in axeslist): return axeslist[(table,entry)]
        if(self.current_table != table):
            self.load_table(table)
        d=createfunc()
        axisname=d["name"]
        axid = cmor.axis(table_entry = axisname,units = d["units"],coord_vals = d["values"],cell_bounds = d["bounds"])
        axeslist[(table,axisname)]=axid
        return axid

    def create_time_axis(self,table,entry,createfunc):
        return create_axis(self,table,self.time_axes,createfunc)

    def create_depth_axis(self,table,entry,createfunc):
        return create_axis(self,table,self.depth_axes,createfunc)

    def create_grid(self,createfunc):
        raise Exception("Not implemented yet")
