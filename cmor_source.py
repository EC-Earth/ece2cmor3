from datetime import timedelta

# Base class for cmor source objects, which represent variables produced by a model
class cmor_source(object):

    def __init__(self):
        self.frequency=datetime.timedelta(0)
        self.spatial_dims=2

    def dims(self):
        return self.spatial_dims

    def freq(self):
        return self.freq

    def grid(self):
        pass

    def realm(self):
        pass

import json
import os

# ECMWF grib code object
class grib_code:
    def __init__(self,var_id_,tab_id_):
        self.var_id=var_id_
        self.tab_id=tab_id_

    def __eq__(self,other):
        return self.var_id==other.var_id and self.tab_id==other.tab_id

    def __str__(self):
        return str(self.var_id)+'.'+str(self.tab_id)

    @classmethod
    def read(cls,istr):
        strpair=istr.split('.')
        if(len(strpair)!=2):
            raise Exception("Invalid input string for grib code:",istr)
        vid=int(strpair[0])
        tid=int(strpair[1])
        cls=grib_code(vid,tid)
        return cls

# Reads a group of grib codes from a json-file
def read_grib_codes_group(file,key):
    s=open(file).read()
    data=json.loads(s)
    if(key in data):
        return [grib_code.read(s) for s in data[key]]
    else:
        return []

# IFS source subclass, constructed from a given grib code.
class ifs_source(cmor_source):

    grib_codes_file=os.path.join(os.path.dirname(__file__),"resources/grib_codes.json")
    grib_codes_3D=read_grib_codes_group(grib_codes_file,"MFP3D")
    grib_codes_2D_dyn=read_grib_codes_group(grib_codes_file,"MFP2DF")
    grib_codes_2D_phy=read_grib_codes_group(grib_codes_file,"MFPPHY")
    grib_codes_extra=read_grib_codes_group(grib_codes_file,"NVEXTRAGB")
    grib_codes=grib_codes_3D+grib_codes_2D_phy+grib_codes_2D_phy+grib_codes_extra

    def __init__(self,code):
        if(not code in ifs_source.grib_codes):
            raise Exception("Unknown grib code passed to IFS source parameter constructor:",str(code.var_id)+"."+str(code.tab_id))
        self.code__=code
        self.spatial_dims=-1
        if(code in ifs_source.grib_codes_3D):
            self.grid_="spec_grid"
            self.spatial_dims=3
        else:
            self.grid_="pos_grid"
            self.spatial_dims=2
        self.realm_="atmos"

    def grid(self):
        return self.grid_

    def realm(self):
        return self.realm_

    def get_grib_code(self):
        return grib_code(self.code__.var_id,self.code__.tab_id)

    @classmethod
    def read(cls,s):
        gc=grib_code.read(s)
        cls=ifs_source(gc)
        return cls

    @classmethod
    def create(cls,vid,tid):
        cls=ifs_source(grib_code(vid,tid))
        return cls

from cmor_utils import cmor_enum

# NEMO grid type enumerable.
# TODO: add scalar grid for soga,masso,volo
nemo_grid=cmor_enum(["grid_U","grid_V","grid_W","grid_T","icemod","SBC"])

# NEMO depth axes dictionary.
nemo_depth_axes={nemo_grid.grid_U:"u",nemo_grid.grid_V:"v",nemo_grid.grid_W:"w",nemo_grid.grid_T:"t"}

# NEMO source subclass, constructed from NEMO output variable id, grid type and dimensions.
# TODO: grid type and dimensions should follow from Nemo's field_def.xml
class nemo_source(cmor_source):

    def __init__(self,var_id_,grid_id_,dims_=-1):
        self.var_id=var_id_
        if(grid_id_>=len(nemo_grid)):
            raise Exception("Invalid grid type passed to nemo source parameter constructor:",grid_id_)
        self.grid_=grid_id_
        self.spatial_dims=dims_

    def grid(self):
        return nemo_grid[self.grid_]

    def realm(self):
        return "ocean"

    def var(self):
        return self.var_id
