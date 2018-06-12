import os
#import io
#import csv
#import gzip
import re
import numpy
import pandas
import datetime
import json
import logging
import netCDF4
import cmor
import cmor_utils
import cmor_source
import cmor_target
import cmor_task

#from ifs2cmor import create_gauss_grid, ref_date_

#from cmor.Test.test_python_open_close_cmor_multiple import path

# Logger object
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
lpjg_files_ = []

# Dictionary of lpjg grid type with cmor grid id.
grid_ids_ = {}

# List of land use tyle ids with ??? cmor grid id ???.
landuse_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}
ref_date_ = datetime.datetime(1850,1,1,0,0,0) #this is the default
cmor_calendar_ = None

lpjg_path_ = None

ncpath_ = None
ncpath_created_ = False


#various things extracted from Michael.Mischurow out2nc tool: ec_earth.py
grids = {
#    32:  [20, 27, 36, 40, 45, 50, 60, 64, 72, 75, 80, 90, 90, 96, 100, 108, 108, 120, 120, 120, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128],
#    48:  [20, 25, 36, 40, 45, 50, 60, 60, 72, 75, 80, 90, 96, 100, 108, 120, 120, 120, 128, 135, 144, 144, 160, 160, 160, 160, 160, 180, 180, 180, 180, 180, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192, 192],
    80:  [18, 25, 36, 40, 45, 54, 60, 64, 72, 72, 80, 90, 96, 100, 108, 120, 120, 128, 135, 144, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 200, 216, 216, 216, 225, 225, 240, 240, 240, 256, 256, 256, 256, 288, 288, 288, 288, 288, 288, 288, 288, 288, 300, 300, 300, 300, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320],
    128: [18, 25, 36, 40, 45, 50, 60, 64, 72, 72, 80, 90, 90, 100, 108, 120, 120, 125, 128, 144, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 216, 225, 240, 240, 240, 250, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 360, 375, 375, 375, 375, 384, 384, 400, 400, 400, 400, 405, 432, 432, 432, 432, 432, 432, 432, 450, 450, 450, 450, 450, 480, 480, 480, 480, 480, 480, 480, 480, 480, 480, 486, 486, 486, 500, 500, 500, 500, 500, 500, 500, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512],
#    160: [18, 25, 36, 40, 45, 50, 60, 64, 72, 72, 80, 90, 90, 96, 108, 120, 120, 125, 128, 135, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 225, 225, 240, 240, 243, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 375, 375, 375, 384, 384, 400, 400, 400, 405, 432, 432, 432, 432, 432, 450, 450, 450, 450, 480, 480, 480, 480, 480, 480, 480, 500, 500, 500, 500, 500, 512, 512, 540, 540, 540, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 576, 576, 576, 576, 600, 600, 600, 600, 600, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640],
#    200: [18, 25, 36, 40, 45, 50, 60, 64, 72, 72, 75, 81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 225, 225, 240, 240, 243, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 320, 360, 360, 360, 360, 360, 360, 375, 375, 375, 384, 400, 400, 400, 400, 432, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 480, 486, 500, 500, 500, 512, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 576, 576, 600, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 640, 640, 640, 648, 648, 675, 675, 675, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 729, 729, 729, 750, 750, 750, 750, 750, 750, 750, 750, 768, 768, 768, 768, 768, 768, 768, 768, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800],
#    256: [18, 25, 32, 40, 45, 50, 60, 64, 72, 72, 75, 81, 90, 96, 100, 108, 120, 120, 125, 135, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 216, 225, 240, 240, 243, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 375, 375, 384, 384, 400, 400, 400, 432, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 486, 500, 500, 500, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 600, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 640, 648, 675, 675, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 720, 720, 729, 729, 750, 750, 750, 750, 750, 768, 768, 768, 768, 800, 800, 800, 800, 800, 800, 800, 800, 810, 810, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 900, 900, 900, 900, 900, 900, 900, 900, 900, 900, 900, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 972, 972, 972, 972, 972, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024],
#    320: [18, 25, 36, 40, 45, 50, 60, 64, 72, 72, 75, 81, 90, 96, 100, 108, 120, 120, 125, 135, 144, 144, 150, 160, 180, 180, 180, 192, 192, 200, 216, 216, 216, 225, 240, 240, 240, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 375, 375, 384, 384, 400, 400, 405, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 486, 500, 500, 500, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 648, 648, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 720, 720, 729, 750, 750, 750, 750, 768, 768, 768, 768, 800, 800, 800, 800, 800, 800, 810, 810, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 900, 900, 900, 900, 900, 900, 900, 900, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 972, 972, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1024, 1024, 1024, 1024, 1024, 1024, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1152, 1152, 1152, 1152, 1152, 1152, 1152, 1152, 1152, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1215, 1215, 1215, 1215, 1215, 1215, 1215, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280],
#    400: [18, 25, 32, 40, 45, 50, 60, 60, 72, 72, 75, 81, 90, 96, 100, 108, 120, 120, 125, 128, 144, 144, 150, 160, 160, 180, 180, 192, 192, 200, 200, 216, 216, 225, 240, 240, 240, 250, 250, 256, 270, 288, 288, 288, 300, 300, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 375, 375, 384, 400, 400, 400, 405, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 486, 500, 500, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 648, 675, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 729, 729, 750, 750, 750, 750, 768, 768, 768, 800, 800, 800, 800, 800, 800, 810, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 900, 900, 900, 900, 900, 900, 900, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 972, 972, 1000, 1000, 1000, 1000, 1000, 1000, 1024, 1024, 1024, 1024, 1024, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1152, 1152, 1152, 1152, 1152, 1152, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1215, 1215, 1215, 1215, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1296, 1296, 1296, 1296, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1458, 1458, 1458, 1458, 1458, 1458, 1458, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600],
#    512: [18, 25, 32, 40, 45, 50, 60, 60, 72, 72, 75, 81, 90, 96, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 225, 225, 240, 240, 243, 250, 256, 270, 270, 288, 288, 288, 300, 320, 320, 320, 320, 360, 360, 360, 360, 360, 360, 375, 375, 384, 384, 400, 400, 400, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 486, 500, 500, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 576, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 648, 675, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 729, 729, 750, 750, 750, 768, 768, 768, 800, 800, 800, 800, 800, 800, 810, 864, 864, 864, 864, 864, 864, 864, 864, 864, 864, 900, 900, 900, 900, 900, 900, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 972, 972, 1000, 1000, 1000, 1000, 1000, 1024, 1024, 1024, 1024, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1152, 1152, 1152, 1152, 1152, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1215, 1215, 1215, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1296, 1296, 1296, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1458, 1458, 1458, 1458, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1620, 1620, 1620, 1620, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1944, 1944, 1944, 1944, 1944, 1944, 1944, 1944, 1944, 1944, 1944, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048],
#    640: [18, 25, 32, 40, 45, 50, 60, 60, 72, 72, 75, 81, 90, 90, 96, 100, 108, 120, 120, 125, 135, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 216, 225, 240, 240, 243, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 360, 360, 360, 360, 360, 360, 375, 375, 384, 384, 400, 400, 400, 432, 432, 432, 432, 450, 450, 450, 480, 480, 480, 480, 480, 486, 500, 500, 512, 512, 540, 540, 540, 540, 540, 576, 576, 576, 576, 576, 600, 600, 600, 600, 640, 640, 640, 640, 640, 640, 640, 648, 675, 675, 675, 675, 720, 720, 720, 720, 720, 720, 720, 720, 729, 750, 750, 750, 750, 768, 768, 768, 800, 800, 800, 800, 800, 810, 810, 864, 864, 864, 864, 864, 864, 864, 864, 900, 900, 900, 900, 900, 900, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 960, 972, 972, 1000, 1000, 1000, 1000, 1000, 1024, 1024, 1024, 1024, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1080, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1125, 1152, 1152, 1152, 1152, 1152, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1215, 1215, 1215, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1280, 1296, 1296, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1440, 1458, 1458, 1458, 1458, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1536, 1536, 1536, 1536, 1536, 1536, 1536, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1620, 1620, 1620, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1920, 1944, 1944, 1944, 1944, 1944, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2025, 2025, 2025, 2025, 2025, 2025, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2160, 2187, 2187, 2187, 2187, 2187, 2187, 2187, 2187, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2250, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2304, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2430, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560, 2560]
}
grids = {i: j+j[::-1] for i, j in grids.items()}

#for ifs2cmor.create_gaus_grid(512,0,ifs_T255_yvals)
ifs_T255_yvals = numpy.array([ 89.46282  , 88.76695  , 88.06697  , 87.36607  , 86.6648   ,
        85.96337  , 85.26185  , 84.56026  , 83.85863  , 83.15699  ,
        82.45532  , 81.75363  , 81.05194  , 80.35023  , 79.64853  ,
        78.94681  , 78.24509  , 77.54337  , 76.84164  , 76.13991  ,
        75.43818  , 74.73644  , 74.03471  , 73.33297  , 72.63123  ,
        71.92949  , 71.22775  , 70.52601  , 69.82426  , 69.12252  ,
        68.42078  , 67.71903  , 67.01729  , 66.31554  , 65.61379  ,
        64.91205  , 64.2103   , 63.50855  , 62.8068   , 62.10506  ,
        61.40331  , 60.70156  , 59.99981  , 59.29806  , 58.59631  ,
        57.89456  , 57.19281  , 56.49106  , 55.78931  , 55.08756  ,
        54.38581  , 53.68406  , 52.98231  , 52.28056  , 51.57881  ,
        50.87706  , 50.17531  , 49.47356  , 48.7718   , 48.07005  ,
        47.3683   , 46.66655  , 45.9648   , 45.26305  , 44.56129  ,
        43.85954  , 43.15779  , 42.45604  , 41.75429  , 41.05254  ,
        40.35078  , 39.64903  , 38.94728  , 38.24553  , 37.54378  ,
        36.84202  , 36.14027  , 35.43852  , 34.73677  , 34.03502  ,
        33.33326  , 32.63151  , 31.92976  , 31.228    , 30.52625  ,
        29.8245   , 29.12275  , 28.42099  , 27.71924  , 27.01749  ,
        26.31573  , 25.61398  , 24.91223  , 24.21048  , 23.50872  ,
        22.80697  , 22.10522  , 21.40347  , 20.70171  , 19.99996  ,
        19.29821  , 18.59645  , 17.8947   , 17.19295  , 16.4912   ,
        15.78944  , 15.08769  , 14.38594  , 13.68418  , 12.98243  ,
        12.28068  , 11.57893  , 10.87717  , 10.17542  , 9.473666 ,
         8.771913 , 8.07016  , 7.368407 , 6.666654 , 5.964901 ,
         5.263148 , 4.561395 , 3.859642 , 3.157889 , 2.456136 ,
         1.754383 , 1.05263  , 0.3508765, -0.3508765, -1.05263  ,
        - 1.754383 , -2.456136 , -3.157889 , -3.859642 , -4.561395 ,
        - 5.263148 , -5.964901 , -6.666654 , -7.368407 , -8.07016  ,
        - 8.771913 , -9.473666 , -10.17542  , -10.87717  , -11.57893  ,
       - 12.28068  , -12.98243  , -13.68418  , -14.38594  , -15.08769  ,
       - 15.78944  , -16.4912   , -17.19295  , -17.8947   , -18.59645  ,
       - 19.29821  , -19.99996  , -20.70171  , -21.40347  , -22.10522  ,
       - 22.80697  , -23.50872  , -24.21048  , -24.91223  , -25.61398  ,
       - 26.31573  , -27.01749  , -27.71924  , -28.42099  , -29.12275  ,
       - 29.8245   , -30.52625  , -31.228    , -31.92976  , -32.63151  ,
       - 33.33326  , -34.03502  , -34.73677  , -35.43852  , -36.14027  ,
       - 36.84202  , -37.54378  , -38.24553  , -38.94728  , -39.64903  ,
       - 40.35078  , -41.05254  , -41.75429  , -42.45604  , -43.15779  ,
       - 43.85954  , -44.56129  , -45.26305  , -45.9648   , -46.66655  ,
       - 47.3683   , -48.07005  , -48.7718   , -49.47356  , -50.17531  ,
       - 50.87706  , -51.57881  , -52.28056  , -52.98231  , -53.68406  ,
       - 54.38581  , -55.08756  , -55.78931  , -56.49106  , -57.19281  ,
       - 57.89456  , -58.59631  , -59.29806  , -59.99981  , -60.70156  ,
       - 61.40331  , -62.10506  , -62.8068   , -63.50855  , -64.2103   ,
       - 64.91205  , -65.61379  , -66.31554  , -67.01729  , -67.71903  ,
       - 68.42078  , -69.12252  , -69.82426  , -70.52601  , -71.22775  ,
       - 71.92949  , -72.63123  , -73.33297  , -74.03471  , -74.73644  ,
       - 75.43818  , -76.13991  , -76.84164  , -77.54337  , -78.24509  ,
       - 78.94681  , -79.64853  , -80.35023  , -81.05194  , -81.75363  ,
       - 82.45532  , -83.15699  , -83.85863  , -84.56026  , -85.26185  ,
       - 85.96337  , -86.6648   , -87.36607  , -88.06697  , -88.76695  ,
       - 89.46282  ])

#extracted from ifs2cmor.py
def create_gauss_grid(nx,x0,yvals):
    ny = len(yvals)
    i_index_id = cmor.axis(table_entry = "i_index",units = "1",coord_vals = numpy.array(range(1,nx + 1)))
    j_index_id = cmor.axis(table_entry = "j_index",units = "1",coord_vals = numpy.array(range(1,ny + 1)))
    dx = 360./nx
    xvals = numpy.array([x0 + (i + 0.5)*dx for i in range(nx)])
    lonarr = numpy.tile(xvals,(ny,1))
    latarr = numpy.tile(yvals[::-1],(nx,1)).transpose()
    lonmids = numpy.array([x0 + i*dx for i in range(nx + 1)])
    latmids = numpy.empty([ny + 1])
    latmids[0] = 90.
    latmids[1:ny] = 0.5*(yvals[0:ny - 1] + yvals[1:ny])
    latmids[ny] = -90.
    vertlats = numpy.empty([ny,nx,4])
    vertlats[:,:,0] = numpy.tile(latmids[0:ny],(nx,1)).transpose()
    vertlats[:,:,1] = vertlats[:,:,0]
    vertlats[:,:,2] = numpy.tile(latmids[1:ny+1],(nx,1)).transpose()
    vertlats[:,:,3] = vertlats[:,:,2]
    vertlons = numpy.empty([ny,nx,4])
    vertlons[:,:,0] = numpy.tile(lonmids[0:nx],(ny,1))
    vertlons[:,:,3] = vertlons[:,:,0]
    vertlons[:,:,1] = numpy.tile(lonmids[1:nx+1],(ny,1))
    vertlons[:,:,2] = vertlons[:,:,1]
    #lons lats added for lpjg
    lons = (lonmids[1:] + lonmids[:-1]) / 2
    lats = (latmids[1:] + latmids[:-1]) / 2
    return cmor.grid(axis_ids = [j_index_id,i_index_id],latitude = latarr,longitude = lonarr,
                     latitude_vertices = vertlats,longitude_vertices = vertlons), lons, lats
#===============================================================================
# def fname(wdir, files):
#     parts = sorted(files, key=lambda x: x.name)
#     for key, grp in itertools.groupby(parts, key=lambda x: x.name):
#         grp = list(grp)
#         if len(grp) == 1:
#             yield grp[0]
#         else:
#             yield combine(wdir, grp)
# 
# def combine(wdir, files):
#     files.sort(key=lambda x: x.parts[-2:-4:-1])
#     handles = [file.open('rb') for file in files]
#     file = tempfile.NamedTemporaryFile(mode='wb', dir=str(wdir), prefix='.',
#             suffix='-'+files[0].parts[-1], delete=False)
#     with file as f:
#         f.write(next(handles[0]))
#         [next(i) for i in handles[1:]]
#         f.writelines(itertools.chain.from_iterable(zip(*handles)))
#     for f in handles:
#         f.close()
#     fname = Path(file.name).resolve()
#     cleanup.add(fname)
#     return fname
#===============================================================================
def rnd(x, digits=3):
    return round(x, digits)

def coords(df, ds, meta, deg, lonmids, latmids):
    # deg is 128 in N128
    # common deg: 32, 48, 80, 128, 160, 200, 256, 320, 400, 512, 640
    # correspondence to spectral truncation:
    # t159 = n80; t255 = n128; t319 = n160; t639 = n320; t1279 = n640
    # i.e. t(2*X -1) = nX
    # number of longitudes in the regular grid: deg * 4
    # At deg >= 319 polar correction might have to be applied (see Courtier and Naughton, 1994)
    #deg = 128
    lons = [lon for num in grids[deg] for lon in numpy.linspace(0, 360, num, False)]
    x, w = numpy.polynomial.legendre.leggauss(deg*2)
    lats = numpy.arcsin(x) * 180 / -numpy.pi
    lats = [lats[i] for i, n in enumerate(grids[deg]) for _ in range(n)]

    i = ds.createDimension('i', len(lons))
    j = ds.createDimension('j', 1)

    latitude = ds.createVariable('lat', 'f4', ('j', 'i'))
    latitude.standard_name = 'latitude'
    latitude.long_name = 'latitude coordinate'
    latitude.units = 'degrees_north'
    # latitude.bounds = 'lat_vertices'
    latitude[:] = lats

    longitude = ds.createVariable('lon', 'f4', ('j', 'i'))
    longitude.standard_name = 'longitude'
    longitude.long_name = 'longitude coordinate'
    longitude.units = 'degrees_east'
    # longitude.bounds = 'lon_vertices'
    longitude[:] = lons

    run_lons = [rnd(i) for i in (df.index.levels[0].values + 360.0) % 360.0]
    run_lats = [rnd(i) for i in df.index.levels[1]]
#    df.index.set_levels([run_lons, run_lats, df.index.levels[2]], inplace=True)
#    df = df.reindex([(rnd(i), rnd(j), k) for i, j, k in zip(lons, lats, df.index.levels[2])], fill_value=meta['missing'])
    df.index.set_levels([run_lons, run_lats], inplace=True)
    df = df.reindex([(rnd(i), rnd(j)) for i, j in zip(lons, lats)], fill_value=meta['missing'])
    return df, ('j', 'i')


# Initializes the processing loop.
def initialize(path,ncpath,expname,tableroot,start,length,refdate):
    global log,lpjg_files_,exp_name_,table_root_
    global lpjg_path_, ncpath_, ncpath_created_
    exp_name_ = expname
    table_root_ = tableroot
    lpjg_path_ = path
    ref_date_ = refdate
    if not ncpath.startswith("/"):
        ncpath_ = os.path.join(lpjg_path_,ncpath)
    else:
        ncpath_ = ncpath
    if not os.path.exists(ncpath_) and not ncpath_created_:
        os.makedirs(ncpath_)
        ncpath_created_ = True
    #lpjg_files_ = select_files(path,expname,start,length)
    cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
    cmor.load_table(tableroot + "_grids.json")
    #log.info("Creating lpjg grids in CMOR...")
    #create_grids() #what should happen here, setup something for the T255 or T159 grid?
    return True


# Resets the module globals.
def finalize():
    global lpjg_files_,grid_ids_,landuse_,time_axes_
    lpjg_files_ = []
    grid_ids_ = {}
    landuse_ = {}
    time_axes_ = {}


# Executes the processing loop.
# used the nemo2cmor.py execute as template
def execute(tasks):
    global log,time_axes_,landuse_,table_root_,lpjg_files_
    global lpjg_path_, ncpath_
    log.info("Executing %d lpjg tasks..." % len(tasks))
    log.info("Cmorizing lpjg tasks...")
    taskdict = cmor_utils.group(tasks,lambda t:t.target.table)
    return #the following parts are not yet fully implemented
    for k,v in taskdict.iteritems():
        tab = k
        tskgroup = v
        files = []
        for task in tskgroup:
            freq = task.target.frequency
            lpjgfiles = task.source.srcpath
            colname = task.source.colname
            outname = task.target.out_name
            outdims = task.target.dimensions
            #FIXME: hardwired T255 grid, moved up here, since create_lpjg_netcdf needs lonmids, latmids for the re-mapping
#            ifs_T255_grid_id, lonmids, latmids = create_gauss_grid(512,0,ifs_T255_yvals)
            #TODO: generate the netCDF file for the requested variable(s)
#            ncfile = create_lpjg_netcdf(freq,colname,lpjgfiles,outname,outdims,lonmids,latmids)
            if ncfile:
                print(ncfile)
                files.append(ncfile)
        
                targetvars = [t.target.variable for t in tskgroup]
                log.info("Loading CMOR table %s to process %d variables..." % (tab,len(targetvars)))
                tab_id = -1
                try:
                    tab_id = cmor.load_table("_".join([table_root_,tab]) + ".json")
                    cmor.set_table(tab_id)
                except:
                    log.error("CMOR failed to load table %s, skipping variables %s" % (tab,str(targetvars)))
                    continue
                log.info("Creating axes for table %s..." % tab)
                axes = []
                #cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")
                #cmor.load_table(table_root_ + "_grids.json")
                
                tgtdims = getattr(task.target,cmor_target.dims_key).split()
                if("latitude" in tgtdims and "longitude" in tgtdims):
                    if(ifs_T255_grid_id != 0):
                        axes.append(ifs_T255_grid_id)
                
                ds = netCDF4.Dataset(ncfile,'r')
                #need to remap to the gaussian grid or already write the netcdf on the gaussian grid
                
                #===============================================================
                # #append grid dimensions FAILS latter with some weird out of val_max error
                # axis_lat=create_grid_axis(task,'lat',ds)
                # axes.append(axis_lat)
                # axis_lon=create_grid_axis(task,'lon',ds)
                # axes.append(axis_lon)
                #===============================================================
                
                time_axes_[tab_id] = create_time_axis(freq,ds)            
                axes.append(time_axes_[tab_id])
                #TODO: add the landuse axes if needed
                varid = create_cmor_variable(task,ds,axes)
                #ncvar = ds.variables[task.source.var()]
                ncvar = ds.variables[task.target.out_name]
                factor = get_conversion_factor(getattr(task,cmor_task.conversion_key,None))
                cmor_utils.netcdf2cmor(varid,ncvar,0,factor,missval = getattr(task.target,cmor_target.missval_key,1.e+20))
                cmor.close(varid)
        
        #section was adapted from nemo: "Creating depth axes for table"
        #the create_lpjg_netcdf above should have created the landuse data in the lpjg ncfile
        #log.info("Creating landuse axes for table %s..." % tab)
        #no idea how that tab_id in connection with landuse should work????
        #if(not tab_id in landuse_):
        #    landuse_[tab_id] = create_landuse_data(tab_id,files)
        
        
        #FIXME: I don't quite understand the following at all
        #I think it is used to add data to a netCDF file in case they are not in it 
        
        #=======================================================================
        # taskmask = dict([t,False] for t in tskgroup)        
        # # Loop over files:
        # for ncf in files:
        #     ds = netCDF4.Dataset(ncf,'r')
        #     axes = []
        #     axes.append(time_axes_[tab_id])
        #     for task in tskgroup:
        #         varid = create_cmor_variable(task,ds,axes)
        #         #ncvar = ds.variables[task.source.var()]
        #         ncvar = ds.variables[tsk.target.out_name]
        #         execute_netcdf_task(task,ds,tab_id)
        #=======================================================================

        #=======================================================================
        #         if(task.source.colname in ds.variables):
        #             if(taskmask[task]):
        #                 log.warning("Ignoring source variable in nc file %s, since it has already been cmorized." % ncf)
        #             else:
        #                 log.info("Cmorizing source variable %s to target variable %s..." % (task.source.colname,task.target.variable))
        #                 execute_netcdf_task(task,ds,tab_id)
        #                 taskmask[task] = True
        # for task,executed in taskmask.iteritems():
        #     if(not executed):
        #         log.error("The source variable %s could not be found in the input lpjg data" % task.source.colname)
        #=======================================================================


#===============================================================================
# Performs a single task.
# def execute_netcdf_task(task,dataset,tableid):
#     #TDOD: change the whole thing to work for lpjg!!!!
#     #since the lpjg netcdf files should be similar to the ifs cdo created ones
#     #this task should not need much adaption, just the lpjg netCDF have to have the same metadata
#     
#     global log,grid_ids_,landuse_,time_axes_
#     
#     #===========================================================================
#     # filepath = getattr(task, "path", None)
#     # if(not filepath):
#     #     log.error("Could not find file containing data for variable %s in table" % (task.target.variable, task.target.table))
#     #     return
#     # storevar = getattr(task, "store_with", None)
#     #===========================================================================
#     
# #    sppath = getattr(task, "sp_path", None)
# #    if(storevar and not sppath):
# #        log.error("Could not find file containing surface pressure for model level variable...skipping variable %s in table %s" % (task.target.variable, task.target.table))
# #        return
# 
#     axes = []
#     grid_id = getattr(task, "grid_id", 0)
#     if(grid_id != 0):
#         axes.append(grid_id)
#     
#     #TODO: some stuff needed for landUse dimension????        
# #    if(hasattr(task, "z_axis_id")):
# #        axes.append(getattr(task, "z_axis_id"))
#     time_id = getattr(task, "time_axis", 0)
#     if(time_id != 0):
#         axes.append(time_id)
#         
#     varid = create_cmor_variable(task,dataset,axes)
#     ncvar = dataset.variables[task.source.var()]
#     factor = get_conversion_factor(getattr(task,cmor_task.conversion_key,None))
#     cmor_utils.netcdf2cmor(varid,ncvar,0,factor,missval = getattr(task.target,cmor_target.missval_key,1.e+20))
#     cmor.close(varid)
#===============================================================================

import math
def distance(row_a, row_b, weights):
    diffs = [math.fabs(a-b) for a,b in zip(row_a, row_b)]
    return sum([v*w for v,w in zip(diffs, weights)])

def get_nearest_neighbour(data, criteria, weights):
    def sort_func(row):
        return distance(row, criteria, weights)
    return min(data, key=sort_func)

def create_lpjg_netcdf(freq,colname,lpjgfiles,outname,outdims,lonmids,latmids):
    global lpjg_path_,ncpath_,ref_date_
    #should lpjg_path be inside the runleg or parent dir?
    lpjgfile = os.path.join(lpjg_path_,lpjgfiles if outdims.find(u"landUse")<0 else lpjgfiles[0])
    #df = _get(lpjgfile,colname,freq) #reads the first lpjgfile lon,lat,time,colname in (somewhat cached)
    df = pandas.read_csv(lpjgfile, delim_whitespace=True, dtype=numpy.float64, compression='infer')    
    daterange, timevals, timebnds = get_lpjg_time_info(df,freq) #date range of the 1st file is used
    #df = df.unstack()
    startdate = str(daterange[0])[0:4]+str(daterange[0])[5:7]
    enddate = str(daterange[1])[0:4]+str(daterange[1])[5:7]
    ncfile = os.path.join(ncpath_,outname+"_"+freq+"_"+startdate+"_"+enddate+".nc") #TODO: add time information e.g. cSoil_yr_187001_187912.nc, similar to IFS 
    print("create_lpjg_netcdf "+colname+" into "+ncfile)
    #should check if file was already generated and just return the ncfile name
    #if os.path.isfile(ncfile):
    #    return ncfile
    print(lpjgfiles)
    #if not generate the file and return the ncfile name
    if (outdims.find(u"landUse")>=0):
        print("TODO: aggregate the landcovers to the LUMIP landUse")
        if freq == u"yr": #yearly
            print("and create yearly netcdf")
        else: #monthly
            print("and create monthly netcdf")                    
    else:
        print("yearly" if freq == u"yr" else "monthly" +" output")
        if freq == u"yr": #yearly
            print("read data and create yearly netcdf")
            meta = { "missing" : netCDF4.default_fillvals['f4'] } #from out2nc
                        
            df1=df.loc[df['Year'] == min(df['Year'])]
            dflons = (df1["Lon"] + 360.0) % 360.0 #numpy.array(df.index.levels[0].values) + 360.0 ) % 360.0
            dflats = df1["Lat"] #numpy.array(df.index.levels[1].values)
            ilon = []
            for lon in dflons:
                idx = numpy.abs(lonmids-lon).argmin()
                ilon.append(idx)
            
            ilat = []
            for lat in dflats:
                idx = numpy.abs(latmids-lat).argmin()
                ilat.append(idx)
                
            years=df["Year"].unique()
            tmp=numpy.empty((len(latmids),len(lonmids),len(years)))
            tmp.fill(netCDF4.default_fillvals['f4'])
        #    tmp.fill(1)
            #timevals = []
            for iyr in range(0,len(years)):
                df1=df.loc[df['Year'] == years[iyr]]
            #    timevals.append(datetime.datetime(int(years[iyr]),1,1,0,0,0))
                vals=df1[colname].values
                for i in range(0,len(vals)):
                    ix=ilon[i]
                    iy=ilat[i]
                    val=vals[i]
                    if (iy < tmp.shape[0] and ix < tmp.shape[1]):
                        tmp[iy,ix,iyr] = val
                        #print(str(years[iyr]) + " " + str(iyr) + " " + str(ix) + " " + str(iy) + " = " + str(val))
                    else:
                        print("NOPE " + str(years[iyr]) + " " + str(iyr) + " " + str(ix) + " " + str(iy) + " = " + str(val))
                        
            ds = netCDF4.Dataset(ncfile, 'w') #, format=meta.get('format', 'NETCDF4_CLASSIC'))
            time = ds.createDimension('time', None)
            timev = ds.createVariable('time', 'f4', ('time',),  )
            timev.calendar = "proleptic_gregorian" #cmor.get_cur_dataset_attribute("calendar")
            timev.units = 'days since {}-01-01'.format(ref_date_.year)
            timev[:] = netCDF4.date2num(timevals,timev.units,timev.calendar)            

            #CHECK: the time bnds
            bnds = ds.createDimension('bnds', 2)
            timebndsv = ds.createVariable('time_bnds', 'f4', ('time','bnds'))
            timebndsv[:] = netCDF4.date2num(timebnds,timev.units,timev.calendar).T
            timev.bounds = "time_bnds"
            
            dlon = ds.createDimension('lon',len(lonmids))
            dlat = ds.createDimension('lat',len(latmids))
            latv = ds.createVariable('lat', 'f4', ('lat',))
            lonv = ds.createVariable('lon', 'f4', ('lon',))
            latv[:] = latmids
            lonv[:] = lonmids
            
            datav = ds.createVariable(outname,'f4',('time','lon','lat'), fill_value=netCDF4.default_fillvals['f4'])
            datav[:] = tmp.T
            
            ds.sync()
            ds.close()
            
        else: #monthly
            print("TODO: read data and create monthly netcdf")            
    return ncfile

def get_lpjg_data(lpjgfile,colname,freq):
    df=_get(lpjgfile,colname,freq)        
    return df

def find_lpjg_output(path,expname=None,filemode="(out.gz|out)"):
    #filemode: "out.gz" or "out" or "(out.gz|out)"
    subexpr=".*"
    expr=re.compile(subexpr+filemode)
    result = []
    for root,dirs,files in os.walk(path):
        result.extend([os.path.join(root,f) for f in files if re.match(expr,f)])
    return result

def get_lpjg_time_info(df,freq):
    timevals = None
    startend = (None,None)        
    if freq == "yr":
        timevals = pandas.unique(df["Year"].values) #df.index.levels[2].values
        timedates = []
        timestart = []
        timeend = []
        for yr in timevals: # we take the 1-jan as reference, shodul we take the middle of the year?
            timedates.append(datetime.datetime(int(yr),1,1,0,0,0)) #ref middle of year?
            timestart.append(datetime.datetime(int(yr),1,1,0,0,0))
            timeend.append(datetime.datetime(int(yr),12,31,23,59,59))
        timebnds = [timestart,timeend]
        minYear=int(min(timevals))
        maxYear=int(max(timevals))
        startend=(datetime.datetime(minYear,1,1,0,0,0),datetime.datetime(maxYear,12,31,23,59,59))
    elif freq == "mon":   
        timevals = pandas.unique(df["Year"].values) ##we only have full years df.index.levels[2].values
        timedates = []
        timestart = []
        timeend = []
        for yr in timevals:
            for mon in range(1,12):
                timedates.append(datetime.datetime(int(yr),mon,1,0,0,0)) #middle of month?
                timestart.append(datetime.datetime(int(yr),mon,1,0,0,0))
                timeend.append(datetime.datetime(int(yr),mon+1,1,23,59,59)-datetime.timedelta(days=1))
        timebnds = [timestart,timeend]
        minYear=int(min(timevals))
        maxYear=int(max(timevals))
        startend=(datetime.datetime(minYear,1,1,0,0,0),datetime.datetime(maxYear,12,31,23,59,59))
    else: #daily ???
        timevals = None
        timebnds = None
        startend = (None,None)        
    
    return startend, timedates, timebnds
# 
# def get_lpjg_time_info(df,freq):
#     timevals = None
#     startend = (None,None)        
#     if freq == "yr":
#         timevals = df["Year"] #df.index.levels[2].values
#         timedates = []
#         timestart = []
#         timeend = []
#         for yr in timevals: # we take the 1-jan as reference, shodul we take the middle of the year?
#             timedates.append(datetime.datetime(int(yr),1,1,0,0,0)) #ref middle of year?
#             timestart.append(datetime.datetime(int(yr),1,1,0,0,0))
#             timeend.append(datetime.datetime(int(yr),12,31,23,59,59))
#         timebnds = [timestart,timeend]
#         minYear=int(min(timevals))
#         maxYear=int(max(timevals))
#         startend=(datetime.datetime(minYear,1,1,0,0,0),datetime.datetime(maxYear,12,31,23,59,59))
#     elif freq == "mon":   
#         timevals = df["Year"] ##we only have full years df.index.levels[2].values
#         timedates = []
#         timestart = []
#         timeend = []
#         for yr in timevals:
#             for mon in range(1,12):
#                 timedates.append(datetime.datetime(int(yr),mon,1,0,0,0)) #middle of month?
#                 timestart.append(datetime.datetime(int(yr),mon,1,0,0,0))
#                 timeend.append(datetime.datetime(int(yr),mon+1,1,23,59,59)-datetime.timedelta(days=1))
#         timebnds = [timestart,timeend]
#         minYear=int(min(timevals))
#         maxYear=int(max(timevals))
#         startend=(datetime.datetime(minYear,1,1,0,0,0),datetime.datetime(maxYear,12,31,23,59,59))
#     else: #daily ???
#         timevals = None
#         timebnds = None
#         startend = (None,None)        
#     
#     return startend, timedates, timebnds
    

def _get(fname, colname, freq):
    df = cache.get(fname)
    if df is not None:
        if colname in df:
            return df.pop(colname)
        raise ValueError('{} not found in {}'.format(colname, fname))

    idx_col = ([0, 1, 2, 3] if freq=="daily" else [0, 1, 2]) if freq=="yr" or freq=="mon" else [0, 1]
    df = pandas.read_csv(fname, delim_whitespace=True, index_col=idx_col, dtype=numpy.float64, compression='infer')

    #df.rename(columns=lambda x: x.lower(), inplace=True)

    if freq=="daily":
        if df.shape[1] != 1:
            raise ValueError('Multiple columns in the daily file are not supported')
        return df.unstack()
    if freq=="mon":
        return df
    cache[fname] = df
    return _get(fname, colname, freq)
cache = {}



# Unit conversion utility method
def get_conversion_factor(conversion):
    #TDOD: update for lpjg!!!
    global log
    if(not conversion): return 1.0
    #if(conversion == "tossqfix"): return 1.0
    if(conversion == "frac2percent"): return 100.0
    if(conversion == "percent2frac"): return 0.01
    log.error("Unknown explicit unit conversion %s will be ignored" % conversion)
    return 1.0

# Creates a variable in the cmor package
def create_cmor_variable(task,dataset,axes):
    ncvar = dataset.variables[task.target.out_name]
    unit = getattr(ncvar,"units",None)
    if((not unit) or hasattr(task,cmor_task.conversion_key)): # Explicit unit conversion
        unit = getattr(task.target,"units")
    return cmor.variable(table_entry = str(task.target.out_name),units = str(unit),axis_ids = axes,original_name = str(task.source.colname))

# Creates all landUse for the given table from the given files
# used nemo2cmor create_depth_axes as template
def create_landuse_data(tab_id,files):
    global log,exp_name_
    result = {}
    for f in files:        
        #TODO: has the tab_id or look into files lpjg ncfile f the landuse dimensions
        #if yes: need to also create the cmo2 landuse var 
        #FIXME: is the grid check needed?
        gridstr = get_lpjg_grid(f,exp_name_)
        if(not gridstr in cmor_source.lpjg_grid):
            log.error("Unknown lpjg grid %s encountered. Skipping landuse axis creation" % gridstr)
            continue
        index = cmor_source.lpjg_grid.index(gridstr)
        if(not index in cmor_source.lpjg_landuse):
            continue
        if(index in result):
            continue
        did = create_landuse_var(f,cmor_source.lpjg_landuse[index])
        if(did != 0): result[index] = did
    return result


# Creates a cmor landUse dimension/axis
# used nemo2cmor create_depth_axis as template
def create_landuse_var(ncfile,gridchar):
    global log
    ds=netCDF4.Dataset(ncfile)
    varname="landUse"
#    if(not varname in ds.variables):
#        log.error("Could not find landuse axis variable %s in lpjg output file %s; skipping landuse axis creation." % (varname,gridchar))
#        return 0
    landusevar = ds.variables[varname]
#    landusebnd = getattr(landusevar,"bounds")
    units = getattr(landusevar,"units")
#    bndvar = ds.variables[landusebnd]
#    b = bndvar[:,:]
#    b[b<0] = 0
    return cmor.axis(table_entry = "landUse",units = units,coord_vals = landusevar[:],cell_bounds = None)


# Creates a time axis for the corresponding table (which is suppoed to be loaded)
    #===========================================================================
    # datetimes = sorted(set(map(lambda s:datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S"),times)))
    # if(len(datetimes) == 0):
    #     log.error("Empty time step list encountered at time axis creation for files %s" % str(path))
    #     return;
    # refdt = cmor_utils.make_datetime(ref_date_)
    # timconv = lambda d:(cmor_utils.get_rounded_time(freq,d) - refdt).total_seconds()/3600.
    # if(hasbnds):
    #     n = len(datetimes)
    #     bndvar = numpy.empty([n,2])
    #     roundedtimes = map(timconv,datetimes)
    #     bndvar[:,0] = roundedtimes[:]
    #     bndvar[0:n-1,1] = roundedtimes[1:n]
    #     bndvar[n-1,1] = (cmor_utils.get_rounded_time(freq,datetimes[n-1],1) - refdt).total_seconds()/3600.
    #     times[:] = bndvar[:,0] + (bndvar[:,1] - bndvar[:,0])/2
    #     return cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times,cell_bounds = bndvar)
    # times = numpy.array([(d - refdt).total_seconds()/3600 for d in datetimes])
    # return cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times)
    #===========================================================================
def create_time_axis(freq,ds):
    global log, ref_date_
    vals = None
    tname = "time"
    timvar = ds.variables[tname]
    vals = timvar[:]
    units = getattr(timvar,"units", None)        
    if(len(vals) == 0 or units == None):
        log.error("No time values or units could be read from lpjg output file")
        return 0
    calendar = getattr(timvar, "calendar", u"proleptic_gregorian") # or standard        
    datevar = []
    datevar.append(netCDF4.num2date(vals,units = units,calendar = calendar))
    
    bnds = getattr(timvar,"bounds", None)
    if bnds: #FIXME: weird genrated ncfile does not seem to have time_bnds
        bndvar = ds.variables[bnds]
    else:
        #lets fake the time bnds
        n = len(vals)
        bndvar = numpy.empty([n, 2])
        bndvar[:, 0] = vals[:]
        bndvar[0:n - 1, 1] = vals[1:n]
        bndvar[n - 1, 1] = max(vals)+1
    ax_id = cmor.axis(table_entry = "time1",units = units,coord_vals = vals,cell_bounds = bndvar[:,:])
    return ax_id

def create_grid_axis(task,gridname,ds):
    global log
    vals = None
    units = None
    var = ds.variables[gridname]
    vals = var[:]
    if vals.ndim>1:
        vals=vals.flatten()
    #===========================================================================
    # bnds = getattr(var,gridname+"_bnds", None)
    # if bnds:
    #     bndvar = ds.variables[bnds]
    # else:
    #     #lets fake the time bnds
    #     n = len(vals)
    #     bndvar = numpy.empty([n, 2])
    #     bndvar[:, 0] = vals[:]
    #     bndvar[0:n - 1, 1] = vals[1:n]
    #     bndvar[n - 1, 1] = max(vals)+1
    #===========================================================================
    units = getattr(var,"units",None)
    if((not units) or hasattr(task,cmor_task.conversion_key)):
        units = getattr(task.target,"units")        
    if(len(vals) == 0 or units == None):
        log.error("No time values or units could be read from lpjg ncfile %s" % str(ds.name))
        return 0
    ax_id = cmor.axis(table_entry = gridname,units = units,coord_vals = vals,cell_bounds = None)
    return ax_id


#===============================================================================
# # Selects files with data with the given frequency
# #needed for lpjg??
# def select_freq_files(freq):
#     global exp_name_,lpjg_files_
#     lpjgfreq = freq
#     selected = []
#     for f in lpjg_files_:
#         filefreq = get_lpjg_frequency(f)
#         print(f,filefreq)
#         if filefreq == lpjgfreq:
#             selected.append(object)
#     return selected
# #    return [f for f in lpjg_files_ if cmor_utils.get_lpjg_frequency(f) == lpjgfreq]
# 
# 
# # Retrieves all lpjg output files in the input directory.
# def select_files(path,expname,start,length):
#     allfiles = find_lpjg_output(path,expname)
#     starttime = cmor_utils.make_datetime(start)
#     stoptime = cmor_utils.make_datetime(start+length)
#     #lets check the first file for the date and check if it fits to the requested starttime and stoptime
#     result = get_lpjg_time_info(allfiles[0])
#     if result[0] <= stoptime and result[1] >= starttime:
#         return allfiles
#     else:
#         return None
#===============================================================================


#FIXME: is it really needed
def get_lpjg_grid(filepath,expname):
    #hardwired at present.  
    #Is filepath the lpjg netCDF file? then check within the file?  
    return cmor_source.lpjg_grid["grid_T255"]  # or "grid_T159"

# Reads all the lpjg grid data from the input files.
def create_grids():
    global grid_ids_,lpjg_files_
    print("create_grids: What todo here?")
#    spatial_grids = [grd for grd in cmor_source.lpjg_grid if grd != cmor_source.lpjg_grid.scalar]
#    for g in spatial_grids:
#        gridfiles = [f for f in lpjg_files_ if (f.endswith(g + ".out") or f.endswith(g + ".out.gz"))]
#        if(len(gridfiles) != 0):
#            grid = read_grid(gridfiles[0])
#            grid_ids_[g] = write_grid(grid)


# Reads a particular lpjg grid from the given input file.
def read_grid(ncfile):
    ds = netCDF4.Dataset(ncfile,'r')
    lons = ds.variables['lon'][:,:]
    lats = ds.variables['lat'][:,:]
    return lpjggrid(lons,lats)


# Transfers the grid to cmor.
def write_grid(grid):
    nx = grid.lons.shape[0]
    ny = grid.lons.shape[1]
    #nemo is swapped now???
    i_index_id = cmor.axis(table_entry = "j_index",units = "1",coord_vals = numpy.array(range(1,nx + 1)))
    j_index_id = cmor.axis(table_entry = "i_index",units = "1",coord_vals = numpy.array(range(1,ny + 1)))
    if(ny == 1):
        return cmor.grid(axis_ids = [i_index_id],
                latitude = grid.lats[:,0],
                longitude = grid.lons[:,0],
                latitude_vertices = grid.vertex_lats,
                longitude_vertices = grid.vertex_lons)
    return cmor.grid(axis_ids = [i_index_id,j_index_id],
                     latitude = grid.lats,
                     longitude = grid.lons,
                     latitude_vertices = grid.vertex_lats,
                     longitude_vertices = grid.vertex_lons)

    
# Class holding a lpjg grid, including bounds arrays
class lpjggrid(object):

    def __init__(self,lons_,lats_):
        flon = numpy.vectorize(lambda x:x % 360)
        flat = numpy.vectorize(lambda x:(x + 90) % 180 - 90)
        self.lons = flon(lpjggrid.smoothen(lons_))
        self.lats = flat(lats_)
        self.vertex_lons = lpjggrid.create_vertex_lons(lons_)
        self.vertex_lats = lpjggrid.create_vertex_lats(lats_)

    @staticmethod
    def create_vertex_lons(a):
        nx = a.shape[0]
        ny = a.shape[1]
        b = numpy.zeros([nx,ny,4])
        f = numpy.vectorize(lambda x:x % 360)
        b[1:nx,:,0]=f(0.5 * (a[0:nx - 1,:] + a[1:nx,:]))
        b[0,:,0] = b[nx - 1,:,0]
        b[0:nx - 1,:,1] = b[1:nx,:,0]
        b[nx - 1,:,1] = b[1,:,1]
        b[:,:,2] = b[:,:,1]
        b[:,:,3] = b[:,:,0]
        return b

    @staticmethod
    def create_vertex_lats(a):
        nx = a.shape[0]
        ny = a.shape[1]
        b = numpy.zeros([nx,ny,4])
        f = numpy.vectorize(lambda x:(x + 90) % 180 - 90)
        b[:,0,0] = f(1.5 * a[:,0] - 0.5 * a[:,1])
        b[:,1:ny,0] = f(0.5 * (a[:,0:ny - 1] + a[:,1:ny]))
        b[:,:,1] = b[:,:,0]
        b[:,0:ny - 1,2] = b[:,1:ny,0]
        b[:,ny - 1,2] = f(1.5 * a[:,ny - 1] - 0.5 * a[:,ny - 2])
        b[:,:,3] = b[:,:,2]
        return b

    @staticmethod
    def modlon2(x,a):
        if(x < a): return x + 360.0
        else: return x

    @staticmethod
    def smoothen(a):
        nx = a.shape[0]
        ny = a.shape[1]
        mod = numpy.vectorize(lpjggrid.modlon2)
        b = numpy.empty([nx,ny])
        for i in range(0,nx):
            x = a[i,1]
            b[i,0] = a[i,0]
            b[i,1] = x
            b[i,2:] = mod(a[i,2:],x)
        return b
