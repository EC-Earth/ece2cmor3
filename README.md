[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1051094.svg)](https://doi.org/10.5281/zenodo.1051094)

ECE2CMOR3 Python code to CMORize and post-process EC-Earth output data.

## Required python packages:

* cmor-3.7.1 (see cmor [dependencies](https://anaconda.org/conda-forge/cmor/files))
* eccodes/gribapi (for filtering IFS output GRIB files)
* dreq (the CMIP6 data request tool drq)
* netCDF4
* cdo (version 2.1.1; only for atmosphere post-processing)
* pip (for installing python packages)
* f90nml (only for fortran namelist I/O)
* openpyxl (for reading *.xlsx excel sheets)
* XlsxWriter (for writing *.xlsx excel sheets)

## Installation:

More extensive installation description can be found [here](https://dev.ec-earth.org/projects/cmip6/wiki/Installation_of_ece2cmor3) at the EC-Earth portal, including the link to an [example of running ece2cmor](https://dev.ec-earth.org/projects/cmip6/wiki/Step-by-step_guide_for_making_CMIP6_experiments#Cmorisation-with-ece2cmor-v120). The basic ece2cmor3 installation description follows below.

#### Installation & running with Mamba (strongly recommended):
With the `Mamba` package manager all the packages (mostly python in our case) can be installed within one go. For instance, this is certainly beneficial at HPC systems where permissions to install complementary python packages to the default python distribution are lacking.

##### Define a mambapath & two aliases

First, define a `mambapath` and two aliases in a `.bashrc` file for later use:
 ```shell
 mambapath=${HOME}/mamba/
 alias activatemamba='source ${mambapath}/etc/profile.d/conda.sh'
 alias activateece2cmor3='activatemamba; conda activate ece2cmor3'
 ```

##### If Mamba is not yet installed:

Download [mamba](https://github.com/conda-forge/miniforge/releases/latest/) by using `wget` and install it via the commandline with `bash`:
 ```shell
 # Check whether mambapath is set:
 echo ${mambapath}
 # Create a backup of an eventual mamba install (and environments) to prevent an accidental overwrite:
 if [ -d ${mambapath} ]; then backup_label=backup-`date +%d-%m-%Y`; mv -f  ${mambapath} ${mambapath/mamba/mamba-${backup_label}}; fi
 
 # Download & install mamba:
 mkdir -p ${HOME}/Downloads; cd ${HOME}/Downloads/
 wget "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
 bash Mambaforge-$(uname)-$(uname -m).sh -b -u -p ${mambapath}
 
 # Update mamba:
 activatemamba
 mamba update -y --name base mamba
 ```


##### Download ece3cmor3 by a git checkout

For example we create the directoy `${HOME}/cmorize/` for the ece2cmor tool:

```shell
cd ${HOME}/cmorize/
git clone https://github.com/EC-Earth/ece2cmor3.git
cd ece2cmor3
git submodule update --init --recursive
./download-b2share-dataset.sh ./ece2cmor3/resources/b2share-data
```
Note that Github depricates the `https` clone method, therefore see how to [migrate from https to ssh](https://github.com/EC-Earth/ece2cmor3/wiki/instruction-how-to-change-from-https-to-ssh).

##### Creating ece2cmor3 environment via mamba:
In the ece2cmor3 git checkout directory, type
```shell
activatemamba                             # The mamba-activate alias (as defined above)
cd ${HOME}/cmorize/ece2cmor3              # Navigate to the ece2cmor3 root directory
mamba env create -f environment.yml       # Create the python environment (for linux & mac os)
conda activate ece2cmor3                  # Here conda is still used instead of mamba
pip install .                             # Install the ece2cmor3 package
conda deactivate                          # Deactivating the active (here ece2cmor3) environment
```

##### Running ece2cmor3 from its environment:

Some basic tests:
```shell
 activateece2cmor3
  which mamba                              # ${mambapath}/condabin/mamba
  which conda                              # ${mambapath}/condabin/conda
  which python                             # ${mambapath}/envs/ece2cmor3/bin/python
  mamba --version                          # mamba 1.4.4 & conda 23.1.0
  python --version                         # Python 3.11.4
  cdo -V                                   # version 2.2.0
  drq -v                                   # version 01.02.00
  ece2cmor -V                              # ece2cmor v2.1.0
  ece2cmor -h
  drq -h
  checkvars -h
 conda deactivate
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

Use the `-e` for the developer mode, i.e. code changes are immediately active:
```shell
activateece2cmor3
cd ${HOME}/cmorize/ece2cmor3
pip install -e .
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

## Design:

The package consists for 2 main modules, ifs2cmor and nemo2cmor. The main api module ece2cmorlib calls initialization and processing functions in these ocean and atmosphere specific codes. The full workload is divided into tasks, which consist of a source (an IFS grib code or NEMO parameter id) and a target (a cmor3 CMIP6 table entry). The tasks are constructed by the Fortran namelist legacy loader (namloader.py) or by the new json-loader (default). The working is similar to the previous ece2cmor tool: the loader reads parameter tables and creates tasks as it receives a dictionary of desired targets from the caller script.

At execution, the nemo2cmor module searches for the sources in the NEMO output files and streams the data to cmor to rewrite it according to CMIP6 conventions. For the IFS component, the module first performs the necessary post-processing steps, creating a list of intermediate netcdf files that contain time-averaged selections of the data. Special treatment such as unit conversions and post-processing formulas are attached to the tasks as attributes, as well as the file path in which the source data resides.
