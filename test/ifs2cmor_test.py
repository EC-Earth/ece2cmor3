import datetime
import shutil

import cmor
import dateutil
import logging
import netCDF4
import numpy
import os
import unittest

from ece2cmor3 import ifs2cmor, ece2cmorlib

logging.basicConfig(level=logging.DEBUG)

calendar_ = "proleptic_gregorian"

tmp_path = os.path.join(os.path.dirname(__file__), "tmp")


def write_postproc_timestamps(filename, startdate, refdate, interval, offset=0):
    path = os.path.join(ifs2cmor.temp_dir_, filename)
    root = netCDF4.Dataset(path, "w")
    times = []
    time = startdate + interval * offset
    while time.year == startdate.year:
        times.append(time)
        time += interval
    root.createDimension("time", len(times))
    time_variable = root.createVariable("Time", "f8", dimensions=("time",))
    units = "hours since %s" % str(refdate)
    setattr(time_variable, "units", units)
    setattr(time_variable, "calendar", calendar_)
    time_variable[:] = netCDF4.date2num(times, units=units, calendar=calendar_)
    return root, len(times)


class ifs2cmor_tests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = "/tmp/ece2cmor3/ifs2cmor_test"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        self.startdate = datetime.datetime(1950, 1, 1)
        self.refdate = datetime.datetime(1850, 1, 1)
        ece2cmorlib.initialize()
        cmor.set_cur_dataset_attribute("calendar", calendar_)

    @staticmethod
    def test_prev_month_find():
        exp = "pmt1"
        fnames = ["ICM" + t + exp + "+" + dt for t in ["GG", "SH"] for dt in ["000000", "185001", "184912"]]
        path1 = os.path.join(tmp_path, "prev_mon_test_src", "001")
        path2 = os.path.join(tmp_path, "prev_mon_test_dst")
        try:
            os.makedirs(path1, exist_ok=True)
            for fname in fnames:
                open(os.path.join(path1, fname), 'a').close()
            os.makedirs(path2, exist_ok=True)
            for fname in fnames:
                os.symlink(os.path.join(path1, fname), os.path.join(path2, fname))
            ifs2cmor.find_grib_files(exp, path1)
            prevfile = ifs2cmor.ifs_preceding_files_[os.path.join(path1, "ICMGG" + exp + "+185001")]
            assert prevfile in [os.path.join(path2, "ICMGG" + exp + "+184912"),
                                os.path.join(path1, "ICMGG" + exp + "+184912")]
            initfile = ifs2cmor.ifs_preceding_files_[os.path.join(path1, "ICMGG" + exp + "+184912")]
            assert initfile == os.path.join(path1, "ICMGG" + exp + "+000000")
        finally:
            shutil.rmtree(os.path.join(tmp_path, "prev_mon_test_src"))
            shutil.rmtree(path2)

    @staticmethod
    def test_ini_month_find():
        exp = "pmt2"
        fnames = ["ICM" + t + exp + "+" + dt for t in ["GG", "SH"] for dt in ["000000", "185001"]]
        path1 = os.path.join(tmp_path, "prev_mon_test_src", "001")
        path2 = os.path.join(tmp_path, "prev_mon_test_dst", "001")
        try:
            os.makedirs(path1, exist_ok=True)
            for fname in fnames:
                open(os.path.join(path1, fname), 'a').close()
            os.makedirs(path2, exist_ok=True)
            for fname in fnames:
                if not os.path.exists(os.path.join(path2, fname)):
                    os.symlink(os.path.join(path1, fname), os.path.join(path2, fname))
            ifs2cmor.find_grib_files(exp, path2)
            inifile = ifs2cmor.ifs_preceding_files_[os.path.join(path2, "ICMGG" + exp + "+185001")]
            assert inifile == os.path.join(path2, "ICMGG" + exp + "+000000")
        finally:
            shutil.rmtree(path1)
            shutil.rmtree(path2)

    @staticmethod
    def test_discard_exp_backups():
        exp = "pmt2"
        fnames_001 = ["ICM" + t + exp + "+" + dt for t in ["GG", "SH"] for dt in ["000000", "185012"]]
        fnames_002 = ["ICM" + t + exp + "+" + dt for t in ["GG", "SH"] for dt in ["185101"]]
        try:
            for leg, fnames in zip(['001', '002'], [fnames_001, fnames_002]):
                path1 = os.path.join(tmp_path, leg)
                path2 = os.path.join(tmp_path, f'{leg}_backup')
                path3 = os.path.join(tmp_path, leg, "backup")
                for p in [path1, path2, path3]:
                    os.makedirs(p, exist_ok=True)
                    for fname in fnames:
                        open(os.path.join(p, fname), 'a').close()
            ifs2cmor.find_grib_files(exp, os.path.join(tmp_path, '001'))
            inifile = ifs2cmor.ifs_preceding_files_[os.path.join(tmp_path, '001', f'ICMGG{exp}+185012')]
            assert inifile == os.path.join(tmp_path, '001', f'ICMGG{exp}+000000')
            ifs2cmor.find_grib_files(exp, os.path.join(tmp_path, '002'))
            inifile = ifs2cmor.ifs_preceding_files_[os.path.join(tmp_path, '002', f'ICMGG{exp}+185101')]
            assert inifile == os.path.join(tmp_path, '001', f'ICMGG{exp}+185012')
        finally:
            for leg, fnames in zip(['001', '002'], [fnames_001, fnames_002]):
                path1 = os.path.join(tmp_path, leg)
                path2 = os.path.join(tmp_path, f'{leg}_backup')
                for p in [path1, path2]:
                    shutil.rmtree(p)

    def test_monthly_time_axis(self):
        ifs2cmor.temp_dir_ = self.temp_dir
        ifs2cmor.ref_date_ = self.refdate
        ifs2cmor.start_date_ = self.startdate
        interval = dateutil.relativedelta.relativedelta(months=1)
        ncroot, numtimes = write_postproc_timestamps("rsds_Amon.nc", self.startdate, self.refdate, interval)
        ncvar = ncroot.createVariable("rsds", "f8", dimensions=("time",))
        ncvar[:] = numpy.full((numtimes,), -1.23)
        filepath = ncroot.filepath()
        ncroot.close()
        cmor.load_table("CMIP6_Amon.json")
        axisid, lower_bnds, upper_bnds = ifs2cmor.create_time_axis(freq="mon", path=filepath, name="time",
                                                                   has_bounds=True)
        assert lower_bnds == [self.startdate + n * interval for n in range(0, 12)]
        assert upper_bnds == [self.startdate + n * interval for n in range(1, 13)]
        os.remove(filepath)

    def test_daily_time_axis(self):
        ifs2cmor.temp_dir_ = self.temp_dir
        ifs2cmor.ref_date_ = self.refdate
        ifs2cmor.start_date_ = self.startdate
        interval = dateutil.relativedelta.relativedelta(days=1)
        ncroot, numtimes = write_postproc_timestamps("rsds_day.nc", self.startdate, self.refdate, interval)
        ncvar = ncroot.createVariable("rsds", "f8", dimensions=("time",))
        ncvar[:] = numpy.full((numtimes,), -1.23)
        filepath = ncroot.filepath()
        ncroot.close()
        cmor.load_table("CMIP6_day.json")
        axisid, lower_bnds, upper_bnds = ifs2cmor.create_time_axis(freq="day", path=filepath, name="time",
                                                                   has_bounds=True)
        assert lower_bnds == [self.startdate + n * interval for n in range(0, 365)]
        assert upper_bnds == [self.startdate + n * interval for n in range(1, 366)]
        os.remove(filepath)

    def test_6hr_time_axis(self):
        ifs2cmor.temp_dir_ = self.temp_dir
        ifs2cmor.ref_date_ = self.refdate
        ifs2cmor.start_date_ = self.startdate
        interval = dateutil.relativedelta.relativedelta(hours=6)
        ncroot, numtimes = write_postproc_timestamps("bs550aer_6hr.nc", self.startdate, self.refdate, interval)
        ncvar = ncroot.createVariable("bs550aer", "f8", dimensions=("time",))
        ncvar[:] = numpy.full((numtimes,), -1.23)
        filepath = ncroot.filepath()
        ncroot.close()
        cmor.load_table("CMIP6_6hrLev.json")
        axisid, lower_bnds, upper_bnds = ifs2cmor.create_time_axis(freq="6hr", path=filepath, name="time",
                                                                   has_bounds=True)
        assert lower_bnds == [self.startdate + n * interval for n in range(0, 4 * 365)]
        assert upper_bnds == [self.startdate + n * interval for n in range(1, 4 * 365 + 1)]
        os.remove(filepath)

    def test_3hr_time_axis(self):
        ifs2cmor.temp_dir_ = self.temp_dir
        ifs2cmor.ref_date_ = self.refdate
        ifs2cmor.start_date_ = self.startdate
        interval = dateutil.relativedelta.relativedelta(hours=3)
        ncroot, numtimes = write_postproc_timestamps("rsds_3hr.nc", self.startdate, self.refdate, interval)
        ncvar = ncroot.createVariable("rsds", "f8", dimensions=("time",))
        ncvar[:] = numpy.full((numtimes,), -1.23)
        filepath = ncroot.filepath()
        ncroot.close()
        cmor.load_table("CMIP6_3hr.json")
        axisid, lower_bnds, upper_bnds = ifs2cmor.create_time_axis(freq="3hr", path=filepath, name="time",
                                                                   has_bounds=True)
        assert lower_bnds == [self.startdate + n * interval for n in range(0, 8 * 365)]
        assert upper_bnds == [self.startdate + n * interval for n in range(1, 8 * 365 + 1)]
        os.remove(filepath)

    def test_6hrPt_time_axis(self):
        ifs2cmor.temp_dir_ = self.temp_dir
        ifs2cmor.ref_date_ = self.refdate
        ifs2cmor.start_date_ = self.startdate
        interval = dateutil.relativedelta.relativedelta(hours=6)
        ncroot, numtimes = write_postproc_timestamps("ta_6hrPlevPt.nc", self.startdate, self.refdate, interval)
        ncvar = ncroot.createVariable("ta", "f8", dimensions=("time",))
        ncvar[:] = numpy.full((numtimes,), 273.2)
        filepath = ncroot.filepath()
        ncroot.close()
        cmor.load_table("CMIP6_6hrPlevPt.json")
        axisid, lower_bnds, upper_bnds = ifs2cmor.create_time_axis(freq="6hrPt", path=filepath, name="time1",
                                                                   has_bounds=False)
        assert lower_bnds == [self.startdate + n * interval for n in range(0, 4 * 365)]
        assert upper_bnds == lower_bnds
        os.remove(filepath)
