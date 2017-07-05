import os
import glob
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

data_files = []
directories = ('resources/', 'resources/cmip6-cmor-tables/', 'resources/cmip6-cmor-tables/Tables/')
for directory in directories:
    files = [f for f in glob.glob(directory+'*') if os.path.isfile(f)]
    data_files.append(('lib/python2.7/site-packages/' + directory, files))

setup(name="ece2cmor3",
      version="0.0.1",
      author="Gijs van den Oord",
      author_email="g.vandenoord@esciencecenter.nl",
      description="CMORize and post-process EC-Earth output data",
      license="Apache License, Version 2.0",
      url="https://github.com/goord/ece2cmor3",
      packages=find_packages(exclude=('tests', 'examples')),
      py_modules=("cdoapi", "cmorapi", "cmor_source", "cmor_target", "cmor_task", "cmor_utils", "ece2cmorlib", "ece2cmor", "ifs2cmor", "jsonloader", "namloader", "nemo2cmor", "postproc"),
      data_files=data_files,
      include_package_data=True,
      long_description=read('README.md'),
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Science/Research",
                   "Programming Language :: Python",
                   "Operating System :: OS Independent",
                   "Topic :: Utilities",
                   "Topic :: Scientific/Engineering :: Atmospheric Science",
                   "License :: OSI Approved :: Apache Software License",
                   ],
      )
