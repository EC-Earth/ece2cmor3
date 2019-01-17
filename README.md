[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1051094.svg)](https://doi.org/10.5281/zenodo.1051094)

ECE2CMOR3 Python code to CMORize and post-process EC-Earth output data.

## Required python packages:

* netCDF4
* cmor-3.4.0 (see cmor [dependencies](https://anaconda.org/conda-forge/cmor/files))
* cdo (version 1.9.5; only for atmosphere post-processing)
* eccodes/gribapi (for filtering IFS output GRIB files)
* nose, testfixtures (only for testing)
* f90nml (only for fortran namelist I/O)
* xlrd (for reading *.xlsx excel sheets)
* XlsxWriter (for writing *.xlsx excel sheets)

## Installation:

#### Installation & running with anaconda (strongly recommended):
The Anaconda python distribution should be installed. With anaconda all the packages can be installed within one go by the package manager conda. This applies also to systems where one is not allowed to install complementary python packages to the default python distribution.

##### If Anaconda is not yet installed:

Download [anaconda](https://www.anaconda.com/download/) (e.g. take the latest anaconda version for python 2.7) by using wget and:
 ```shell
 wget http://repo.continuum.io/archive/Anaconda2-5.3.0-Linux-x86_64.sh
 bash Anaconda2-5.3.0-Linux-x86_64.sh
 source ${HOME}/.bashrc
 ```
The anaconda installation optionally adds the anaconda python to your $PATH by appending a line to your .bashrc. Commenting this appended line and resourcing the .bashrc gives the default python back.


##### Download ece3cmor3 by a git checkout

For example we create the directoy ${HOME}/cmorize/ for the ece2cmor tool:

```shell
git clone https://github.com/EC-Earth/ece2cmor3.git
cd ece2cmor3
git submodule update --init --recursive
```

##### Creating a virtual conda environment and installing ece3cmor3 therein:
In the ece2cmor3 git checkout directory, type
```shell
conda env create -f environment.yml       # for linux & mac os
source activate ece2cmor3
python setup.py install
```

##### Running ece2cmor3 inside the conda environment:

```shell
 source activate ece2cmor3
 ece2cmor -h
 checkvars -h
 etc.
```

#### Note that the nested CMOR tables require an update once in a while: 

The CMOR tables are maintained via a nested git repository inside the ece2cmor3 git repository. 
Once in a while one of the ece2cmor3 developers will update the nested repository of the CMOR tables. 
This will be visible from the ece2cmor3 repository by a git status call, it will tell that there are "new updates" in these tables. 
In that case one has to repeat the following inside the git checkout directory:
```shell
git submodule update --init --recursive
```

#### Note for developers: 

To avoid many installation calls during development, you can symlink the installed modules to the source directory by executing
```shell
python setup.py develop;
```

#### Updating the nested CMOR table repository by maintainers:
Navigate to your git checkout directory and execute
```shell
cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/tables/
git pull origin master
cd ../; git add cmip6-cmor-tables
git commit cmip6-cmor-tables -m 'Update the nested CMOR tables for their updates'
git push
```

#### Installation with pip:
Alternatively create a virtual python environment with virtualenv. Download the CMOR3 source (https://github.com/PCMDI/cmor/releases) and follow instructions (configure,make,make install). Inside the CMOR source directory run
```shell
python setup.py install
```
to install the python wrapper in your python environment.
Finally run
```shell
pip install requirements.txt
```
to install the remaining dependencies


## Design:

The package consists for 2 main modules, ifs2cmor and nemo2cmor. The main api module ece2cmorlib calls initialization and processing functions in these ocean and atmosphere specific codes. The full workload is divided into tasks, which consist of a source (an IFS grib code or NEMO parameter id) and a target (a cmor3 CMIP6 table entry). The tasks are constructed by the Fortran namelist legacy loader (namloader.py) or by the new json-loader (default). The working is similar to the previous ece2cmor tool: the loader reads parameter tables and creates tasks as it receives a dictionary of desired targets from the caller script.

At execution, the nemo2cmor module searches for the sources in the NEMO output files and streams the data to cmor to rewrite it according to CMIP6 conventions. For the IFS component, the module first performs the necessary post-processing steps, creating a list of intermediate netcdf files that contain time-averaged selections of the data. Special treatment such as unit conversions and post-processing formulas are attached to the tasks as attributes, as well as the file path in which the source data resides.
