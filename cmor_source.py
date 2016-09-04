import json
import os

class cmor_source(object):

    def __init__(self):
        self.grid=None
        self.dims=0
        self.realm=None


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


def read_grib_codes_group(file,key):
    s=open(file).read()
    data=json.loads(s)
    if(key in data):
        return [grib_code.read(s) for s in data[key]]
    else:
        return []


class ifs_source(cmor_source):

    grib_codes_file=os.path.join(os.path.dirname(__file__),'resources/grib_codes.json')
    grib_codes_3D=read_grib_codes_group(grib_codes_file,'MFP3D')
    grib_codes_2D_dyn=read_grib_codes_group(grib_codes_file,'MFP2DF')
    grib_codes_2D_phy=read_grib_codes_group(grib_codes_file,'MFPPHY')
    grib_codes_extra=read_grib_codes_group(grib_codes_file,'NVEXTRAGB')
    grib_codes=grib_codes_3D+grib_codes_2D_phy+grib_codes_2D_phy+grib_codes_extra

    def __init__(self,code):
        if(not code in ifs_source.grib_codes):
            raise Exception("Unknown grib code passed to IFS source parameter constructor:",code)
        self.code__=code
        if(code in ifs_source.grib_codes_3D):
            self.grid="spec_grid"
            self.dims=3
        else:
            self.grid="pos_grid"
            self.dims=2
        self.realm="atmos"

    @classmethod
    def create(cls,s):
        gc=grib_code.read(s)
        cls=ifs_source(gc)
        return cls

    @classmethod
    def create(cls,vid,tid):
        cls=ifs_source(grib_code(vid,tid))
        return cls
