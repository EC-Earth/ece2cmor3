ECE2CMOR3 Python code to CMORize and post-process EC-Earth output data.

## Required python packages:

* netCDF4
* cmor3
* cdo (only for atmosphere post-processing)
* nose (only for testing)
* testfixtures (only for testing)
* python-dateutil
* f90nml (only for namelist loading)
* xlrd (for reading *.xlsx excel sheets)
* XlsxWriter (for writing *.xlsx excel sheets)

## Installation:

#### Installation & running with anaconda (strongly recommended):
The Anaconda python distribution should be installed. With anaconda all the packages can be installed within one go by the package manager conda. This applies also to systems were one is not allowed to install complementary python packages to the default python distribution.

##### If Anaconda is not yet installed:

Downlaod anaconda from: https://www.anaconda.com/download/ (e.g. the latest version for python 2.7), and
 ```shell
 cd Downloads/
 chmod u+x Anaconda2-5.0.0.1-Linux-x86_64.sh
 ./Anaconda2-5.0.0.1-Linux-x86_64.sh
 source ${HOME}/.bashrc
 ```
The anaconda installation added the anaconda python to your $PATH by appending a line to your .bashrc. Commenting this appended line and resourcing the .bashrc gives the default python back.


##### Download ece3cmor3 by a git checkout

For example we create the directoy {HOME}/cmorize/ for the ece2cmor tool:

```shell
mkdir -p ${HOME}/cmorize/; cd ${HOME}/cmorize/
git clone https://github.com/goord/ece2cmor3.git
git submodule update --init --recursive
```

##### Creating a virtual Anaconda environment and installing ece3cmor3 therein:

```shell
cd ${HOME}/cmorize/ece2cmor3/
conda env create -f environment.yml
source activate ece2cmor3
python setup.py install
source deactivate
```

##### Running ece2cmor3 inside the Anaconda environment:

```shell
 source activate ece2cmor3
 cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/
 ./ece2cmor.py -h
 ./scripts/checkvars.py -h
```


#### Note for developers: 

For instance in case one is developing the checkvars.py script which uses the ece2cmor3 package, after any change in the ece2cmor code the line below has to be repeated in order to reload the ece2cmor3 package:
```shell
 cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
```

#### Installation with pip:
Alternatively create a virtual python environment with virtualenv. Download the CMOR3 source (https://github.com/PCMDI/cmor/releases) and follow instructions (configure,make,make install). Inside the CMOR source directory run
```shell
python setup.py install
```
to install the python wrapper in your python environment. Finally run
```shell
pip install requirements.txt
```
to install the remaining dependencies

## Usage:
See the scripts in the examples folder.

## Design:

The package consists for 2 main modules, ifs2cmor and nemo2cmor. The main api module ece2cmorlib calls initialization and processing functions in these ocean and atmosphere specific codes. The full workload is divided into tasks, which consist of a source (an IFS grib code or NEMO parameter id) and a target (a cmor3 CMIP6 table entry). The tasks are constructed by the Fortran namelist legacy loader (namloader.py) or by the new json-loader (to be constructed). The working is similar to the previous ece2cmor tool: the loader reads parameter tables and creates tasks as it receives a dictionary of desired targets from the caller script.

At execution, the nemo2cmor module searches for the sources in the NEMO output files and streams the data to cmor to rewrite it according to CMIP6 conventions. For the IFS component, the module first performs the necessary post-processing steps, creating a list of intermediate netcdf files that contain time-averaged selections of the data. Special treatment such as unit conversions and post-processing formulas are attached to the tasks as attributes, as well as the file path in which the source data resides.
