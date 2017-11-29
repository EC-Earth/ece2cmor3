import os
import io
import csv
import gzip
import numpy
import datetime
import json
import logging
import netCDF4
import cmor
import cmor_utils
import cmor_source
import cmor_target
import cmor_task
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
def rnd(x, digits=6):
    return round(x, digits)

def coords(df, ds, meta):
    # deg is 128 in N128
    # common deg: 32, 48, 80, 128, 160, 200, 256, 320, 400, 512, 640
    # correspondence to spectral truncation:
    # t159 = n80; t255 = n128; t319 = n160; t639 = n320; t1279 = n640
    # i.e. t(2*X -1) = nX
    # number of longitudes in the regular grid: deg * 4
    # At deg >= 319 polar correction might have to be applied (see Courtier and Naughton, 1994)
    deg = 128
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

    run_lons = [rnd(i) for i in (df.index.levels[0].values + 360) % 360]
    run_lats = [rnd(i) for i in df.index.levels[1]]
    df.index.set_levels([run_lons, run_lats], inplace=True)
    df = df.reindex([(rnd(i), rnd(j)) for i, j in zip(lons, lats)], fill_value=meta['missing'])

    return df, ('j', 'i')


# Initializes the processing loop.
def initialize(path,ncpath,expname,tableroot,start,length):
    global log,lpjg_files_,exp_name_,table_root_
    global lpjg_path_, ncpath_, ncpath_created_
    exp_name_ = expname
    table_root_ = tableroot
    lpjg_path_ = path
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
    for k,v in taskdict.iteritems():
        tab = k
        tskgroup = v
        files = []
        for tsk in tskgroup:
            freq = tsk.target.frequency
            lpjgfiles = tsk.source.srcpath
            colname = tsk.source.colname
            outname = tsk.target.out_name
            outdims = tsk.target.dimensions
            #TODO: generate the netCDF file for the requested variable(s)
            ncfile = create_lpjg_netcdf(freq,colname,lpjgfiles,outname,outdims)
            if ncfile: 
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

        log.info("Creating time axes for table %s..." % tab)
        time_axes_[tab_id] = create_time_axis(freq,files)
        
        #section was adapted from nemo: "Creating depth axes for table"
        #the create_lpjg_netcdf above should have created the landuse data in the lpjg ncfile
        #log.info("Creating landuse axes for table %s..." % tab)
        #no idea how that tab_id in connection with landuse should work????
        #if(not tab_id in landuse_):
        #    landuse_[tab_id] = create_landuse_data(tab_id,files)
        
        #FIXME: I don't quite understand the following at all
        #I think it is used to add data to a netCDF file in case they are not in it 
        taskmask = dict([t,False] for t in tskgroup)        
        # Loop over files:
        for ncf in files:
            ds = netCDF4.Dataset(ncf,'r')
            for task in tskgroup:
                if(task.source.colname in ds.variables):
                    if(taskmask[task]):
                        log.warning("Ignoring source variable in nc file %s, since it has already been cmorized." % ncf)
                    else:
                        log.info("Cmorizing source variable %s to target variable %s..." % (task.source.colname,task.target.variable))
                        execute_netcdf_task(task,ds,tab_id)
                        taskmask[task] = True
        for task,executed in taskmask.iteritems():
            if(not executed):
                log.error("The source variable %s could not be found in the input lpjg data" % task.source.colname)


# Performs a single task.
def execute_netcdf_task(task,dataset,tableid):
    #TDOD: change the whole thing to work for lpjg!!!!
    #since the lpjg netcdf files should be similar to the ifs cdo created ones
    #this task should not need much adaption, just the lpjg netCDF have to have the same metadata
    
    global log,grid_ids_,landuse_,time_axes_
    
    filepath = getattr(task, "path", None)
    if(not filepath):
        log.error("Could not find file containing data for variable %s in table" % (task.target.variable, task.target.table))
        return
    storevar = getattr(task, "store_with", None)
    
#    sppath = getattr(task, "sp_path", None)
#    if(storevar and not sppath):
#        log.error("Could not find file containing surface pressure for model level variable...skipping variable %s in table %s" % (task.target.variable, task.target.table))
#        return

    axes = []
    grid_id = getattr(task, "grid_id", 0)
    if(grid_id != 0):
        axes.append(grid_id)
    
    #TODO: some stuff needed for landUse dimension????        
#    if(hasattr(task, "z_axis_id")):
#        axes.append(getattr(task, "z_axis_id"))
    time_id = getattr(task, "time_axis", 0)
    if(time_id != 0):
        axes.append(time_id)
        
    varid = create_cmor_variable(task,dataset,axes)
    ncvar = dataset.variables[task.source.var()]
    factor = get_conversion_factor(getattr(task,cmor_task.conversion_key,None))
    cmor_utils.netcdf2cmor(varid,ncvar,0,factor,missval = getattr(task.target,cmor_target.missval_key,1.e+20))
    cmor.close(varid)

def create_lpjg_netcdf(freq,colname,lpjgfiles,outname,outdims):
    global lpjg_path_,ncpath_
    #should opath be inside the runleg or where?
    lpjgfile = os.path.join(lpjg_path_,lpjgfiles if outdims.find(u"landUse")<0 else lpjgfiles[0])
    daterange = cmor_utils.get_lpjg_interval(lpjgfile) #date range of the 1st file is used
    startdate = str(daterange[0])[0:4]+str(daterange[0])[5:7]
    enddate = str(daterange[1])[0:4]+str(daterange[1])[5:7]
    ncfile = os.path.join(ncpath_,outname+"_"+freq+"_"+startdate+"_"+enddate+".nc") #TODO: add time information e.g. cSoil_yr_187001_187912.nc, similar to IFS 
    print("create_lpjg_netcdf "+colname+" into "+ncfile)
    #should check if file was already generated and just return the ncfile name
    if os.path.isfile(ncfile):
        return ncfile
    print(lpjgfiles)
    #if not generate the file and return the ncfile name
    if (outdims.find(u"landUse")<0):
        print("yearly" if freq == u"yr" else "monthly" +" output")
        if freq == u"yr": #yearly
            print("TODO: read data and create yearly netcdf")
        else: #monthly
            print("TODO: read data and create monthly netcdf")            
    else:
        print("TODO: aggregate the landcovers to the LUMIP landUse")
        if freq == u"yr": #yearly
            print("and create yearly netcdf")
        else: #monthly
            print("and create monthly netcdf")            
    return ncfile


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
    srcvar = task.source.var()
    ncvar = dataset.variables[srcvar]
    unit = getattr(ncvar,"units",None)
    if((not unit) or hasattr(task,cmor_task.conversion_key)): # Explicit unit conversion
        unit = getattr(task.target,"units")
    if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar),positive = "down")
    else:
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar))

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


# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(freq,files):
    global log
    vals = None
    units = None
    ds = None
    for ncfile in files:
        try:
            ds = netCDF4.Dataset(ncfile)
            timvar = ds.variables["time"]
            vals = timvar[:]
            bnds = getattr(timvar,"time_bnds", None)
            if bnds:
                bndvar = ds.variables[bnds]
            else:
                #lets fake the time bnds
                n = len(vals)
                bndvar = numpy.empty([n, 2])
                bndvar[:, 0] = vals[:]
                bndvar[0:n - 1, 1] = vals[1:n]
                bndvar[n - 1, 1] = max(vals)+1
            units = getattr(timvar,"units")
            break
        except:
            if(ds):
                ds.close()
    if(len(vals) == 0 or units == None):
        log.error("No time values or units could be read from lpjg output files %s" % str(files))
        return 0
    ax_id = cmor.axis(table_entry = "time",units = units,coord_vals = vals,cell_bounds = bndvar[:,:])
    return ax_id


# Selects files with data with the given frequency
#needed for lpjg??
def select_freq_files(freq):
    global exp_name_,lpjg_files_
    lpjgfreq = freq
    selected = []
    for f in lpjg_files_:
        filefreq = cmor_utils.get_lpjg_frequency(f)
        print(f,filefreq)
        if filefreq == lpjgfreq:
            selected.append(object)
    return selected
#    return [f for f in lpjg_files_ if cmor_utils.get_lpjg_frequency(f) == lpjgfreq]


# Retrieves all lpjg output files in the input directory.
def select_files(path,expname,start,length):
    allfiles = cmor_utils.find_lpjg_output(path,expname)
    starttime = cmor_utils.make_datetime(start)
    stoptime = cmor_utils.make_datetime(start+length)
    #lets check the first file for the date and check if it fits to the requested starttime and stoptime
    result = cmor_utils.get_lpjg_interval(allfiles[0])
    if result[0] <= stoptime and result[1] >= starttime:
        return allfiles
    else:
        return None


# Reads the calendar attribute from the lpjgfile header (Monthly if Headers are Jan Feb) 
def read_calendar(lpjgfile):
    fileio = None
    if (lpjgfile.endswith(".gz")):
        fptr = gzip.open(lpjgfile, "r")
        fileio = io.BufferedReader(fptr) #python3: io.TextIOWrapper(fptr, newline="")
    else:
        fileio = io.open(lpjgfile, newline="")
    result = None
    if fileio:
        reader = csv.reader(fileio, delimiter=" ", skipinitialspace=True)
        print(list(reader))
        for row in reader:
            print(row['first_name'], row['last_name'])
            #check for Dec and return "monthly" else "yearly"
        result = "monthly" if row.endswith("Dec") else "yearly"
    return result
#    ds = netCDF4.Dataset(ncfile,'r')
#    if(not ds):
#        return None
#    timvar = ds.variables["time_centered"]
#    if(timvar):
#        result = getattr(timvar,"calendar")
#        ds.close()
#        return result
#    else:

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
    lons = ds.variables['nav_lon'][:,:]
    lats = ds.variables['nav_lat'][:,:]
    return lpjggrid(lons,lats)


# Transfers the grid to cmor.
def write_grid(grid):
    nx = grid.lons.shape[0]
    ny = grid.lons.shape[1]
    i_index_id = cmor.axis(table_entry = "i_index",units = "1",coord_vals = numpy.array(range(1,nx + 1)))
    j_index_id = cmor.axis(table_entry = "j_index",units = "1",coord_vals = numpy.array(range(1,ny + 1)))
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
