import logging
import unittest
import os
import nose.tools
import nemo2cmor
import test_utils
import cmor_source
import cmor_target
import cmor_task
import ifs2cmor
import postproc

logging.basicConfig(level=logging.DEBUG)

def get_table_path(tab_id = None):
    directory = os.path.join(os.path.dirname(cmor_target.__file__),"resources","tables")
    return os.path.join(directory,"CMIP6_" + tab_id + ".json") if tab_id else directory

class ifs2cmor_tests(unittest.TestCase):

    def test_postproc_gridmean(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(79,128)
        target = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"clwvi_cfDay.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-setgridtype,regular -daymean -selcode,79")

    def test_postproc_gridmeans(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source1 = cmor_source.ifs_source.create(79,128)
        target1 = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task1 = cmor_task.cmor_task(source1,target1)
        source2 = cmor_source.ifs_source.create(164,128)
        target2 = [t for t in targets if t.variable == "clt" and t.table == "day"][0]
        task2 = cmor_task.cmor_task(source2,target2)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task1,task2])
        path = os.path.join(os.getcwd(),"clt_day.nc")
        nose.tools.eq_(getattr(task2,"path"),path)
        nose.tools.eq_(getattr(task1,"cdo_command"),"-setgridtype,regular -daymean -selcode,79")

    def test_postproc_specmean(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(130,128)
        target = [t for t in targets if t.variable == "ta" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"ta_Amon.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-sp2gpl -monmean -selcode,130")

    def test_postproc_specgrid(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source1 = cmor_source.ifs_source.create(130,128)
        target1 = [t for t in targets if t.variable == "ta" and t.table == "Amon"][0]
        task1 = cmor_task.cmor_task(source1,target1)
        source2 = cmor_source.ifs_source.create(79,128)
        target2 = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task2 = cmor_task.cmor_task(source2,target2)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task1,task2])
        nose.tools.eq_(getattr(task1,"cdo_command"),"-sp2gpl -monmean -selcode,130")
        nose.tools.eq_(getattr(task2,"cdo_command"),"-setgridtype,regular -daymean -selcode,79")

    def test_postproc_daymax(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(165,128)
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"sfcWindmax_day.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-daymax -setgridtype,regular -selcode,165")

    def test_postproc_tasmax(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(201,128)
        target = [t for t in targets if t.variable == "tasmax" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"tasmax_Amon.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-monmean -daymax -setgridtype,regular -selcode,201")

    def test_postproc_windspeed(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.read("var88=sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWind" and t.table == "6hrPlevpt"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"sfcWind_6hrPlevpt.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-expr,'var88=sqrt(sqr(var165)+sqr(var166))' -setgridtype,regular -selhour,0,6,12,18 -selcode,165,166")

    def test_postproc_maxwindspeed(self):
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.read("var88=sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source,target)
        postproc.apply_cdo = False
        ifs2cmor.postprocess([task])
        path = os.path.join(os.getcwd(),"sfcWindmax_day.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"-daymax -expr,'var88=sqrt(sqr(var165)+sqr(var166))' -setgridtype,regular -selcode,165,166")
