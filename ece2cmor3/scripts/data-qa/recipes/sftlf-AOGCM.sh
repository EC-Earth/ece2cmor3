#!/bin/bash
# Thomas Reerink
#
# This scripts needs no argument:
#
# ${1} the first   argument is the 
#
#
# Run example:
#  ./sftlf-AOGCM.sh
#
# With this script the 
#

if [ "$#" -eq 0 ]; then
    
    rm -rf CMIP6
    scp     sftlf_fx_EC-Earth3-Veg_TEMPLATE_r1i1p1f1_gr.nc sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
   #dncdiff sftlf_fx_EC-Earth3-Veg_TEMPLATE_r1i1p1f1_gr.nc sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc

    ncatted -Oh -a Conventions,global,o,c,"CF-1.7 CMIP-6.2"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
   #ncatted -Oh -a activity_id,global,o,c,"CMIP"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                                  ## will be adjusted by sftlf.py
   #ncatted -Oh -a branch_method,global,o,c,"standard"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                            ## will be adjusted by sftlf.py
    ncatted -Oh -a branch_time,global,o,c,"0."  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
   #ncatted -Oh -a branch_time_in_child,global,o,c,"0."  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                           ## will be adjusted by sftlf.py
   #ncatted -Oh -a branch_time_in_parent,global,o,c,"0."  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                          ## will be adjusted by sftlf.py
    ncatted -Oh -a comment,global,o,c,"Production: Thomas Reerink at KNMI"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a contact,global,o,c,"cmip6-data@ec-earth.org"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a creation_date,global,o,c,"2019-09-30T10:38:23Z"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                ## ?
    ncatted -Oh -a data_specs_version,global,o,c,"01.00.31"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a experiment,global,o,c,"all-forcing simulation of the recent past"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc              ## will be adjusted by sftlf.py
    ncatted -Oh -a experiment_id,global,o,c,"historical"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                          ## will be adjusted by sftlf.py
   #ncatted -Oh -a external_variables,global,o,c,"areacella"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
  ##ncatted -Oh -a forcing_index,global,o,c,"1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a frequency,global,o,c,"fx"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
   #ncatted -Oh -a further_info_url,global,o,c,"https://furtherinfo.es-doc.org/CMIP6.EC-Earth-Consortium.EC-Earth3.historical.none.r1i1p1f1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc          ## will be adjusted by sftlf.py
    ncatted -Oh -a grid,global,o,c,"T255L91"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a grid_label,global,o,c,"gr"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a history,global,o,c,"2019-09-30T10:31:03Z ; CMOR rewrote data to be consistent with CMIP6, CF-1.7 CMIP-6.2 and CF standards.;\n processed by ece2cmor v1.2.0, git rev. 85ffde4a22948560fae15bc2dedfc91a3d473d30\n "  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
  ##ncatted -Oh -a initialization_index,global,o,c,"1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a institution,global,o,c,"AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, Denmark; ENEA, Italy; FMI, Finland; Geomar, Germany; ICHEC, Ireland; ICTP, Italy; IDL, Portugal; IMAU, The Netherlands; IPMA, Portugal; KIT, Karlsruhe, Germany; KNMI, The Netherlands; Lund University, Sweden; Met Eireann, Ireland; NLeSC, The Netherlands; NTNU, Norway; Oxford University, UK; surfSARA, The Netherlands; SMHI, Sweden; Stockholm University, Sweden; Unite ASTR, Belgium; University College Dublin, Ireland; University of Bergen, Norway; University of Copenhagen, Denmark; University of Helsinki, Finland; University of Santiago de Compostela, Spain; Uppsala University, Sweden; Utrecht University, The Netherlands; Vrije Universiteit Amsterdam, the Netherlands; Wageningen University, The Netherlands. Mailing address: EC-Earth consortium, Rossby Center, Swedish Meteorological and Hydrological Institute/SMHI, SE-601 76 Norrkoping, Sweden"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a institution_id,global,o,c,"EC-Earth-Consortium"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a mip_era,global,o,c,"CMIP6"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a nominal_resolution,global,o,c,"100 km"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a parent_activity_id,global,o,c,"CMIP"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a parent_experiment_id,global,o,c,"piControl"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                    ## will be adjusted by sftlf.py
    ncatted -Oh -a parent_mip_era,global,o,c,"CMIP6"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a parent_source_id,global,o,c,"EC-Earth3"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                        ## EC-Earth3
   #ncatted -Oh -a parent_time_units,global,o,c,"days since 1850-01-01"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                           ## will be adjusted by sftlf.py
    ncatted -Oh -a parent_variant_label,global,o,c,"r1i1p1f1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
  ##ncatted -Oh -a physics_index,global,o,c,"1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a product,global,o,c,"model-output"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
  ##ncatted -Oh -a realization_index,global,o,c,"1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a realm,global,o,c,"atmos"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a source,global,o,c,"EC-Earth3 (2019): \n aerosol: none\n atmos: IFS cy36r4 (TL255, linearly reduced Gaussian grid equivalent to 512 x 256 longitude/latitude; 91 levels; top level 0.01 hPa)\n atmosChem: none\n land: HTESSEL (land surface scheme built in IFS)\n landIce: none\n ocean: NEMO3.6 (ORCA1 tripolar primarily 1 deg with meridional refinement down to 1/3 degree in the tropics; 362 x 292 longitude/latitude; 75 levels; top grid cell 0-1 m)\n ocnBgchem: none\n seaIce: LIM3"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc      ## EC-Earth3
    ncatted -Oh -a source_id,global,o,c,"EC-Earth3"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                               ## EC-Earth3
   #ncatted -Oh -a source_type,global,o,c,"AOGCM"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc                                                 ## will be adjusted by sftlf.py
    ncatted -Oh -a sub_experiment,global,o,c,"none"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a sub_experiment_id,global,o,c,"none"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a table_id,global,o,c,"fx"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a table_info,global,o,c,"Creation Date:(24 July 2019) MD5:70649eeb16bc90c431e35b583fac7375"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc    ## Correct, checked in CMIP6_coordinate.json: "table_date": "24 July 2019"
    ncatted -Oh -a title,global,o,c,"EC-Earth3 output prepared for CMIP6"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
   #ncatted -Oh -a tracking_id,global,o,c,"hdl:21.14100/f829d35a-cc32-4332-a0a5-e2ddbd8260d1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc     ## EC-Earth3
    ncatted -Oh -a variable_id,global,o,c,"sftlf"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a variant_label,global,o,c,"r1i1p1f1"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a license,global,o,c,"CMIP6 model data produced by EC-Earth-Consortium is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (https://creativecommons.org/licenses). Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, including citation requirements and proper acknowledgment. Further information about this data, including some limitations, can be found via the further_info_url (recorded as a global attribute in this file) and at http://www.ec-earth.org. The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law."  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc
    ncatted -Oh -a cmor_version,global,o,c,"3.5.0"  sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc

   #cd {HIOME}/data-qa/recipes/;
    ./sftlf.py
   #dncdiff sftlf_fx_EC-Earth3-Veg_TEMPLATE_r1i1p1f1_gr.nc sftlf_fx_EC-Earth3_TEMPLATE_r1i1p1f1_gr.nc

#ncdump -h /lustre2/projects/model_testing/reerink/cmorised-results/cmor-cmip-piControl/t264/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/piControl/r1i1p1f1/part-1/Amon/hus/gr/v20190712/hus_Amon_EC-Earth3_piControl_r1i1p1f1_gr_225901-225912.nc|grep branch_time_in_
#ncdump -h /lustre3/projects/CMIP6/reerink/cmorised-results/cmor-cmip-historical/h003/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3/historical/r1i1p1f1/part-2/Amon/hus/gr/v20190926/hus_Amon_EC-Earth3_historical_r1i1p1f1_gr_186101-186112.nc|grep branch_time_in_
#ncdump -h /lustre3/projects/CMIP6/reerink/cmorised-results/cmor-cmip-scenario-ssp1-2.6/s126/CMIP6/ScenarioMIP/EC-Earth-Consortium/EC-Earth3/ssp126/r1i1p1f1/Amon/hus/gr/v20190926/hus_Amon_EC-Earth3_ssp126_r1i1p1f1_gr_201501-201512.nc|grep branch_time_in_

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
