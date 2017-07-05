import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="ece2cmor3",
      version="0.0.1",
      author="Gijs van den Oord",
      author_email="g.vandenoord@esciencecenter.nl",
      description="CMORize and post-process EC-Earth output data",
      license="Apache License, Version 2.0",
      url="https://github.com/goord/ece2cmor3",
      packages=find_packages(exclude=('tests', 'examples')),
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
