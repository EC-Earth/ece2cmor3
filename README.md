ECE2CMOR3 Python code to CMORize and post-process EC-Earth output data.

## Required python packages:

* netCDF4
* cmor3
* cdo (only for atmosphere post-processing)
* nose (only for testing)
* testfixtures (only for testing)
* python-dateutil
* f90nml (only for namelist loading)

## Installation:

#### With pip:
Optionally create a virtual python environment with virtualenv. Download the CMOR3 source (https://github.com/PCMDI/cmor/releases) and follow instructions (configure,make,make install). Inside the CMOR source directory run
```shell
python setup.py install
```
to install the python wrapper in your python environment. Finally run
```shell
pip install requirements.txt
```
to install the remaining dependencies

#### With anaconda:
Optionally create a virtual anaconda environment:
```shell
conda env create -f environment.yml
```
or run the conda install command with the environment yaml file as argument.

## Usage:
See the scripts in the examples folder. If you didn't clone the repository with the ```--recursive``` flag, clone the CMIP6 tables by typing
```shell
git submodule update --init --recursive
```

## Design:

The package consists for 2 main modules, ifs2cmor and nemo2cmor. The main api module ece2cmor calls initialization and processing functions in these ocean and atmosphere specific codes. The full workload is divided into tasks, which consist of a source (an IFS grib code or NEMO parameter id) and a target (a cmor3 CMIP6 table entry). The tasks are constructed by the Fortran namelist legacy loader (namloader.py) or by the new json-loader (to be constructed). The working is similar to the previous ece2cmor tool: the loader reads parameter tables and creates tasks as it receives a dictionary of desired targets from the caller script.

At execution, the nemo2cmor module searches for the sources in the NEMO output files and streams the data to cmor to rewrite it according to CMIP6 conventions. For the IFS component, the module first performs the necessary post-processing steps, creating a list of intermediate netcdf files that contain time-averaged selections of the data. Special treatment such as unit conversions and post-processing formulas are attached to the tasks as attributes, as well as the file path in which the source data resides.
