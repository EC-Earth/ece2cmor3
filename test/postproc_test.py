import logging
import os
import unittest

import test_utils
from ece2cmor3 import cmor_source, cmor_target, cmor_task, postproc

logging.basicConfig(level=logging.DEBUG)


class postproc_tests(unittest.TestCase):

    @staticmethod
    def test_postproc_gridmean():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(79, 128)
        target = [t for t in targets if t.variable == "clwvi" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -daymean -selcode,79"

    @staticmethod
    def test_postproc_specmean():
        testdata = os.path.dirname(__file__) + "/test_data/ifsdata/6hr/ICMSHECE3+199001"
        if test_utils.is_lfs_ref(testdata):
            logging.info("Skipping test_postproc_specmean, download test data from lfs first")
            return
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(131, 128)
        target = [t for t in targets if t.variable == "ua" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source, target)
        setattr(task, cmor_task.filter_output_key, [testdata])
        command = postproc.create_command(task)
        assert command.create_command() == "-sp2gpl -daymean -selzaxis,hybrid -selcode,131"

    @staticmethod
    def test_postproc_daymax():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(165, 128)
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-daymax -setgridtype,regular -selcode,165"

    @staticmethod
    def test_postproc_tasmax():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(201, 128)
        target = [t for t in targets if t.variable == "tasmax" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-monmean -daymax -setgridtype,regular -selcode,201"

    @staticmethod
    def test_postproc_windspeed():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.read("var88", "sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWind" and t.table == "6hrPlevPt"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -expr,'var88=sqrt(sqr(var165)+sqr(var166))' " \
                                           "-selhour,0,6,12,18 -selcode,165,166"

    @staticmethod
    def test_postproc_post_expr():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.read("var23", "var126020/var126022", expr_order=1)
        target = [t for t in targets if t.variable == "cdnc" and t.table == "AERmon"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -expr,'var23=var20/var22' -monmean -selzaxis,hybrid " \
                                           "-selcode,20,22"

    @staticmethod
    def test_postproc_post_expr_masked():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.read("var23", "var126020/var126022", expr_order=1, mask_expr="var172>=0.5")
        target = [t for t in targets if t.variable == "cdnc" and t.table == "AERmon"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -expr,'var23=(var20/var22)/(var172>=0.5)' -monmean " \
                                           "-selzaxis,hybrid -selcode,20,22,172"

    @staticmethod
    def test_postproc_maxwindspeed():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.read("var88", "sqrt(sqr(var165)+sqr(var166))")
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-daymax -setgridtype,regular -expr,'var88=sqrt(sqr(var165)+sqr(var166))' " \
                                           "-selcode,165,166"

    @staticmethod
    def test_postproc_wap500():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(135, 128)
        target = [t for t in targets if t.variable == "wap500" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-sp2gpl -daymean -sellevel,50000. -selzaxis,pressure -selcode,135"

    @staticmethod
    def test_postproc_mrsol():
        source = cmor_source.ifs_source.read("118.129", "merge(70*var39,210*var40,720*var41,1890*var42)")
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        target = [t for t in targets if t.variable == "mrsol" and t.table == "Eday"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -setcode,118 -daymean -expr," \
                                           "'var1=70*var39;var2=210*var40;var3=720*var41;var4=1890*var42' -selcode," \
                                           "39,40,41,42"

    @staticmethod
    def test_postproc_mrsol_masked():
        source = cmor_source.ifs_source.read("118.129", "merge(70*var39,210*var40,720*var41,1890*var42)",
                                             mask_expr="var172>=0.5")
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        target = [t for t in targets if t.variable == "mrsol" and t.table == "Eday"][0]
        task = cmor_task.cmor_task(source, target)
        command = postproc.create_command(task)
        assert command.create_command() == "-setgridtype,regular -setcode,118 -daymean -expr,'var1=(70*var39)/(" \
                                           "var172>=0.5);var2=(210*var40)/(var172>=0.5);var3=(720*var41)/(" \
                                           "var172>=0.5);var4=(1890*var42)/(var172>=0.5)' -selcode,39,40,41,42,172"

    @staticmethod
    def test_postproc_tasmax_missval():
        abspath = test_utils.get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        source = cmor_source.ifs_source.create(201, 128)
        target = [t for t in targets if t.variable == "tasmax" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source, target)
        setattr(task, "missval", "0")
        command = postproc.create_command(task)
        assert command.create_command() == "-setmisstoc,0 -monmean -daymax -setgridtype,regular -selcode,201"
