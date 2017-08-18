import logging
import unittest
import os
from ece2cmor3 import postproc
import nose.tools
import test_utils
from ece2cmor3 import cmor_source
from ece2cmor3 import cmor_target
from ece2cmor3 import cmor_task

logging.basicConfig(level=logging.DEBUG)

class ifs2cmor_tests(unittest.TestCase):

    def test_postproc_gridmean(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(79,128)
        target = [t for t in targets if t.variable == "clwvi" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-setgridtype,regular -daymean -selcode,79")

    def test_postproc_specmean(self):
        testdata = os.path.dirname(__file__) + "/test_data/ifsdata/6hr/ICMSHECE3+199001"
        if(test_utils.is_lfs_ref(testdata)):
            logging.info("Skipping test_postproc_specmean, download test data from lfs first")
            return
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(131,128)
        target = [t for t in targets if t.variable == "ua" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source,target)
        setattr(task,"path",testdata)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-sp2gpl -daymean -selzaxis,hybrid -selmon,1 -selcode,131")

    def test_postproc_daymax(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(165,128)
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-daymax -setgridtype,regular -selcode,165")

    def test_postproc_tasmax(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(201,128)
        target = [t for t in targets if t.variable == "tasmax" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-monmean -daymax -setgridtype,regular -selcode,201")

    def test_postproc_windspeed(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.read("var88=sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWind" and t.table == "6hrPlevPt"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-expr,'var88=sqrt(sqr(var165)+sqr(var166))' -setgridtype,regular -selhour,0,6,12,18 -selcode,165,166")

    def test_postproc_maxwindspeed(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.read("var88=sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-daymax -expr,'var88=sqrt(sqr(var165)+sqr(var166))' -setgridtype,regular -selcode,165,166")

    def test_postproc_wap500(self):
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(135,128)
        target = [t for t in targets if t.variable == "wap500" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source,target)
        command = postproc.create_command(task)
        nose.tools.eq_(command.create_command(),"-sp2gpl -daymean -sellevel,50000. -selzaxis,pressure -selcode,135")
