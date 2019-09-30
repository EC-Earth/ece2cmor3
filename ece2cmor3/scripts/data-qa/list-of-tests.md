List of tests
=============

These following tests must be passed by any EC-Earth data set before it is
published on the ESGF data nodes.


- Run `ece2cmor`, check logs for errors  
  (some `ece2cmor` errors may be accepted, see related discussions on
  the EC-Earth Portal and ece2cmor Github page)

- Scripted checks on file-level:

  + empty files or directories:  
    `find . -empty`

  + auxiliary files:  
    `find . -type f ! -name \*.nc`
    (e.g. `*.nc.copy` files)  
    `find . -name '*_r1i1p1f1_g[rn][a-zA-Z0-9]*'` or something like   
    `find . -type f -regextype sed ! -regex '.*/.*_EC-Earth3-Veg_[0-9a-zA-Z]*_r1i1p1f1_g[nr][_0-9-]*\.nc'`
    (temporary files from CMOR library)

  + versions check:  
    `versions.sh -l .` (check present versions)  
    `versions.sh -v vYYYYMMDD .` (set version, dry-run)  
    `versions.sh -v vYYYYMMDD -m .` (set version)

  + Check number of files per year:  
    `files-per-year <FIRST_YEAR> <LAST_YEAR> .`

  + Check number of files per variable:  
    `files-per-variable <VERSION> <VAR_DIRS>`

- Manual check against do-no-publish list  
  (for now, found in [this google document](https://docs.google.com/spreadsheets/d/1b69NCgHSjWNGqalOVWBTdTvXl7R_-EwCRfJqlwYB37Y))

- Fix ocean fraction in `Ofx/sftof` (check out `sftof.py` under `scripts`)
- Fix land fraction in `fx/sftlf` (check under `recipes` for help)

- Suggestion: set all files/directories *read-only* from here on

- Run `nctime`, checking time axes and ranges:  
  `nctcck -p cmip6 -i <ESGINI_DIR> -l <LOG_DIR> <DATA_DIR>`  
  `nctxck -p cmip6 -i <ESGINI_DIR> -l <LOG_DIR> <DATA_DIR>`

- Run `qa-dkrz`, for comprehensive QA checks:  
  checks enabled:
  + DRS, DRS_F, DRS_P
  + CF
  + CNSTY
  + TIME
  + DATA