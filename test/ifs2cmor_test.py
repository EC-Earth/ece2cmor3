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

logging.basicConfig(level=logging.DEBUG)

class ifs2cmor_tests(unittest.TestCase):

    def test_postproc_gridmean(self):
        path = os.path.dirname(cmor_target.__file__) + "/../../input/cmip6/cmip6-cmor-tables/Tables/"
        abspath = os.path.abspath(path)
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(79,128)
        target = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task = cmor_task.cmor_task(source,target)
        ifs2cmor.ifs_gridpoint_file_ = "ICMGG"
        ifs2cmor.postproc([task],False)
        path = os.path.join(os.getcwd(),"ICMGG_day.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"cdo -P 4 -f nc copy -setgridtype,regular -daymean -shifttime,-3hours -selcode,79 ICMGG " + path)

    def test_postproc_gridmeans(self):
        path = os.path.dirname(cmor_target.__file__) + "/../../input/cmip6/cmip6-cmor-tables/Tables/"
        abspath = os.path.abspath(path)
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source1 = cmor_source.ifs_source.create(79,128)
        target1 = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task1 = cmor_task.cmor_task(source1,target1)
        source2 = cmor_source.ifs_source.create(32,128)
        target2 = [t for t in targets if t.variable == "albsn" and t.table == "emDay"][0]
        task2 = cmor_task.cmor_task(source2,target2)
        ifs2cmor.ifs_gridpoint_file_ = "ICMGG"
        ifs2cmor.postproc([task1,task2],False)
        path = os.path.join(os.getcwd(),"ICMGG_day.nc")
        nose.tools.eq_(getattr(task1,"path"),path)
        nose.tools.eq_(getattr(task1,"cdo_command"),"cdo -P 4 -f nc copy -setgridtype,regular -daymean -shifttime,-3hours -selcode,32,79 ICMGG " + path)

    def test_postproc_specmean(self):
        path = os.path.dirname(cmor_target.__file__) + "/../../input/cmip6/cmip6-cmor-tables/Tables/"
        abspath = os.path.abspath(path)
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(133,128)
        target = [t for t in targets if t.variable == "ta" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source,target)
        ifs2cmor.ifs_spectral_file_ = "ICMSH"
        ifs2cmor.postproc([task],False)
        path = os.path.join(os.getcwd(),"ICMSH_mon.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"cdo -P 4 -f nc sp2gpl -monmean -shifttime,-3hours -selcode,133 ICMSH " + path)

    def test_postproc_specgrid(self):
        path = os.path.dirname(cmor_target.__file__) + "/../../input/cmip6/cmip6-cmor-tables/Tables/"
        abspath = os.path.abspath(path)
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source1 = cmor_source.ifs_source.create(133,128)
        target1 = [t for t in targets if t.variable == "ta" and t.table == "Amon"][0]
        task1 = cmor_task.cmor_task(source1,target1)
        source2 = cmor_source.ifs_source.create(79,128)
        target2 = [t for t in targets if t.variable == "clwvi" and t.table == "cfDay"][0]
        task2 = cmor_task.cmor_task(source2,target2)
        ifs2cmor.ifs_spectral_file_ = "ICMSH"
        ifs2cmor.ifs_gridpoint_file_ = "ICMGG"
        ifs2cmor.postproc([task1,task2],False)
        path1 = os.path.join(os.getcwd(),"ICMSH_mon.nc")
        nose.tools.eq_(getattr(task1,"path"),path1)
        nose.tools.eq_(getattr(task1,"cdo_command"),"cdo -P 4 -f nc sp2gpl -monmean -shifttime,-3hours -selcode,133 ICMSH " + path1)
        path2 = os.path.join(os.getcwd(),"ICMGG_day.nc")
        nose.tools.eq_(getattr(task2,"path"),path2)
        nose.tools.eq_(getattr(task2,"cdo_command"),"cdo -P 4 -f nc copy -setgridtype,regular -daymean -shifttime,-3hours -selcode,79 ICMGG " + path2)

    def test_postproc_daymax(self):
        path = os.path.dirname(cmor_target.__file__) + "/../../input/cmip6/cmip6-cmor-tables/Tables/"
        abspath = os.path.abspath(path)
        targets = cmor_target.create_targets(abspath,"CMIP6")
        source = cmor_source.ifs_source.create(165,128)
        target = [t for t in targets if t.variable == "sfcWindmax" and t.table == "day"][0]
        task = cmor_task.cmor_task(source,target)
        ifs2cmor.ifs_gridpoint_file_ = "ICMGG"
        ifs2cmor.postproc([task],False)
        path = os.path.join(os.getcwd(),"ICMGG_daymax.nc")
        nose.tools.eq_(getattr(task,"path"),path)
        nose.tools.eq_(getattr(task,"cdo_command"),"cdo -P 4 -f nc copy -daymax -shifttime,-3hours -setgridtype,regular -selcode,165 ICMGG " + path)
