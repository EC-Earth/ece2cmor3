import logging

from ece2cmor3 import components


def keep_variable(target, model_component, ecearth_config):
    variable = target.variable
    table = target.table

    # If the component producing the variable is not in the configuration anyway, dismiss it
    if ecearth_config in components.ece_configs and model_component not in components.ece_configs.get(ecearth_config):
        return False

    # For tos, look at the requested grid to determine whether it should be nemo or ifs
    if variable == "tos":
        if "areacello" in getattr(target, "area_operator", []):
            return model_component == "nemo"
        if "areacella" in getattr(target, "area_operator", []):
            return model_component == "ifs"

    # For these basic meteorological variables, let them be produced by tm5 for the AER* tables and otherwise ifs
    if variable in ["pfull", "zg", "ps", "tas", "ua", "va"]:
        if table.startswith("AER"):
            return model_component == "tm5"
        else:
            return model_component == "ifs"

    # Soil moisture etc: prefer ifs over lpjguess in all cases (?)
    if variable in ["mrso", "mrsol", "mrsos", "mrro", "mrros", "tsl"]:
        return model_component == "ifs"

    # Carbon-cycle variables only activated in EC-EARTH-CC
    if variable in ["cfc12", "cfc13", "c14", "sf6"]:
        return model_component == "nemo" and ecearth_config == "EC-EARTH-CC"

    return True
