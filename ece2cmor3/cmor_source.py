import os
import re
import json
import datetime
import logging
import cmor_utils

# Logger instance.
log = logging.getLogger(__name__)

# Base class for cmor source objects, which represent variables produced by a model
class cmor_source(object):

    def __init__(self):
        self.frequency = datetime.timedelta(0)
        self.spatial_dims = 2

    def dims(self):
        return self.spatial_dims

    def freq(self):
        return self.freq

    def grid(self):
        pass

    def realm(self):
        pass

# ECMWF grib code object
class grib_code:
    def __init__(self,var_id_,tab_id_ = 128):
        self.var_id = var_id_
        self.tab_id = tab_id_

    def __eq__(self,other):
        return self.var_id == other.var_id and self.tab_id == other.tab_id

    def __str__(self):
        return str(self.var_id) + '.' + str(self.tab_id)

    def __hash__(self):
        return self.var_id + self.tab_id*1000

    @classmethod
    def read(cls,istr):
        s = istr[3:] if istr.startswith("var") else istr
        strpair = s.split('.')
        if(len(strpair) > 2):
            raise Exception("Invalid input string for grib code:",istr)
        vid = int(strpair[0])
        tid = 128 if len(strpair) == 1 else int(strpair[1])
        cls = grib_code(vid,tid)
        return cls

# Reads a group of grib codes from a json-file
def read_grib_codes_group(file,key):
    s = open(file).read()
    data = json.loads(s)
    if(key in data):
        return [grib_code.read(s) for s in data[key]]
    else:
        return []

ifs_grid = cmor_utils.cmor_enum(["point","spec"])
expression_key = "expr"

# IFS source subclass, constructed from a given grib code.
class ifs_source(cmor_source):

    # Existing grib code lists, read from resources.
    grib_codes_file = os.path.join(os.path.dirname(__file__),"resources/grib_codes.json")
    grib_codes_3D = read_grib_codes_group(grib_codes_file,"MFP3D")
    grib_codes_2D_dyn = read_grib_codes_group(grib_codes_file,"MFP2DF")
    grib_codes_2D_phy = read_grib_codes_group(grib_codes_file,"MFPPHY")
    grib_codes_extra = read_grib_codes_group(grib_codes_file,"NVEXTRAGB")
    grib_codes_sh = read_grib_codes_group(grib_codes_file,"ICMSH")
    grib_codes_accum = read_grib_codes_group(grib_codes_file,"ACCUMFLD") # Includes min/max over previous intervals
    grib_codes = grib_codes_3D + grib_codes_2D_dyn + grib_codes_2D_phy + grib_codes_extra

    # Constructor.
    def __init__(self,code):
        global log
        if(not code):
            self.code_ = None
            self.spatial_dims = -1
            self.grid_ = -1
        else:
            if(not code in ifs_source.grib_codes):
                log.error("Unknown grib code %d.%d passed to IFS source parameter constructor" % (code.var_id,code.tab_id))
            self.code_ = code
            self.spatial_dims = -1
            self.grid_ = ifs_grid.spec if code in ifs_source.grib_codes_sh else ifs_grid.point
            self.spatial_dims = 3 if code in (ifs_source.grib_codes_3D + ifs_source.grib_codes_2D_dyn) else 2

    # Returns the grid.
    def grid(self):
        return ifs_grid[self.grid_] if self.grid_ >= 0 else None

    # Returns the grid id.
    def grid_id(self):
        return self.grid_

    # Returns the grib code.
    def get_grib_code(self):
        return grib_code(self.code_.var_id,self.code_.tab_id) if self.code_ else None

    # Returns the argument grib codes in case of a post-processing expression variable.
    def get_root_codes(self):
        if(hasattr(self,"root_codes")):
            return [grib_code(c.var_id,c.tab_id) for c in getattr(self,"root_codes")]
        else:
            return [self.get_grib_code()] if self.code_ else []

    # Creates an instance from the input string s.
    @classmethod
    def read(cls,s):
        global log
        if re.match("^[0-9]{1,3}.[0-9]{3}$",s) or re.match("^[0-9]{1,3}$",s) or re.match("^[0-9]{1,3}$",s):
            gc = grib_code.read(s)
            cls = ifs_source(gc)
        elif re.match("^var[0-9]{1,3}$",s):
            gc = grib_code.read(s[3:])
            cls = ifs_source(gc)
        else:
            varstrs = re.findall("var[0-9]{1,3}",s)
            if(len(varstrs) == 0 or not s.replace(" ","").startswith(varstrs[0] + "=")):
                raise Exception("Unable to read grib codes from expression",s)
            else:
                newcode = grib_code(int(varstrs[0][3:]),128)
                incodes = list(set(map(lambda x:grib_code(int(x[3:]),128),varstrs[1:])))
                cls = ifs_source(None)
                if(s.replace(" ","") != "var134=exp(var152)"):
                    if(newcode in set(ifs_source.grib_codes) - set(ifs_source.grib_codes_extra)):
                        log.error("New expression code %d.%d already reserved for existing output variable" % (newcode.var_id,newcode.tab_id))
                cls.code_ = newcode
                grid = ifs_grid.spec if (len(incodes)>0 and incodes[0] in ifs_source.grib_codes_sh) else ifs_grid.point
                dims = 3 if (len(incodes)>0 and incodes[0] in ifs_source.grib_codes_3D) else 2
                for c in incodes:
                    if(c not in ifs_source.grib_codes):
                        log.error("Unknown grib code %d.%d in expression %s found" % (c.var_id,c.tab_id,s))
                    cgrid = ifs_grid.spec if (c in ifs_source.grib_codes_sh) else ifs_grid.point
                    if(cgrid != grid): log.error("Invalid combination of gridpoint and spectral variables in expression %s" % s)
                    if(c in ifs_source.grib_codes_3D): dims = 3
                cls.grid_ = grid
                cls.spatial_dims = dims
                setattr(cls,"root_codes",incodes)
                setattr(cls,expression_key,s)
        return cls

    # Creates in instance from the input codes.
    @classmethod
    def create(cls,vid,tid = 128):
        cls = ifs_source(grib_code(vid,tid))
        return cls

# NEMO grid type enumerable.
nemo_grid = cmor_utils.cmor_enum(["grid_U","grid_V","grid_W","grid_T","icemod","SBC","scalar","diaptr"])

# NEMO depth axes dictionary.
nemo_depth_axes = {nemo_grid.grid_U:"u",nemo_grid.grid_V:"v",nemo_grid.grid_W:"w",nemo_grid.grid_T:"t",nemo_grid.SBC:"t",nemo_grid.diaptr:"z"}

# NEMO source subclass, constructed from NEMO output variable id, grid type and dimensions.
# TODO: grid type and dimensions should follow from Nemo's field_def.xml
class nemo_source(cmor_source):

    def __init__(self,var_id_,grid_id_,dims_=-1):
        self.var_id = var_id_
        if(grid_id_ >= len(nemo_grid)):
            raise Exception("Invalid grid type passed to nemo source parameter constructor:",grid_id_)
        self.grid_ = grid_id_
        self.spatial_dims = dims_

    def grid(self):
        return nemo_grid[self.grid_]

    def var(self):
        return self.var_id
