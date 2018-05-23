import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

package_data = {}
directories = ("ece2cmor3/resources", "ece2cmor3/resources/tables")
for d in directories:
    files = [os.path.join(d,f) for f in os.listdir(d) if os.path.isfile(os.path.join(d,f))]
    package_data[d] = files

setup(name = "ece2cmor3",
      version = "1.0.0",
      author = "Gijs van den Oord",
      author_email = "g.vandenoord@esciencecenter.nl",
      description = "CMORize and post-process EC-Earth output data",
      license = "Apache License, Version 2.0",
      url = "https://github.com/EC-Earth/ece2cmor3",
      packages = find_packages(exclude=("tests", "examples")),
      package_data = package_data,
      include_package_data = True,
      long_description = read("README.md"),
      entry_points = {"console_scripts": [
          "ece2cmor =  ece2cmor3.ece2cmor:main",
          "checkvars =  ece2cmor3.scripts.checkvars:main",
          "drq2ppt =  ece2cmor3.scripts.drq2ppt:main",
          "fixmonths =  ece2cmor3.scripts.fixmonths:main",
          "splitbalance =  ece2cmor3.scripts.splitbalance:main"
      ]},
      classifiers = ["Development Status :: 3 - Alpha",
                     "Intended Audience :: Science/Research",
                     "Programming Language :: Python",
                     "Operating System :: OS Independent",
                     "Topic :: Utilities",
                     "Topic :: Scientific/Engineering :: Atmospheric Science",
                     "License :: OSI Approved :: Apache Software License"
                     ],
      )
