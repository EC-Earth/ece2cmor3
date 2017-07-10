import os
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

#data_files = []
package_data = {}
directories = ('resources', 'resources/tables')
for d in directories:
    files = [os.path.join(d,f) for f in os.listdir(d) if os.path.isfile(os.path.join(d,f))]
    #data_files.append((os.path.join(get_python_lib(), d), files))
    package_data[d] = files

setup(name="ece2cmor3",
      version="0.0.1",
      author="Gijs van den Oord",
      author_email="g.vandenoord@esciencecenter.nl",
      install_requires=read('requirements.txt').splitlines(),
      description="CMORize and post-process EC-Earth output data",
      license="Apache License, Version 2.0",
      url="https://github.com/goord/ece2cmor3",
      packages=find_packages(exclude=('tests', 'examples')),
      py_modules=("cdoapi", "cmorapi", "cmor_source", "cmor_target", "cmor_task", "cmor_utils", "ece2cmorlib", "ece2cmor", "ifs2cmor", "jsonloader", "namloader", "nemo2cmor", "postproc"),
      #data_files=data_files,
      package_data=package_data,
      include_package_data=True,
      long_description=read('README.md'),
      entry_points={'console_scripts': [
                       'ece2cmor =  ece2cmor:main',
                       ]
                   },
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Science/Research",
                   "Programming Language :: Python",
                   "Operating System :: OS Independent",
                   "Topic :: Utilities",
                   "Topic :: Scientific/Engineering :: Atmospheric Science",
                   "License :: OSI Approved :: Apache Software License",
                   ],
      )
