import logging

from ece2cmor3 import components, cmor_target


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


def choose_variable(target_list, model_component, ecearth_config):
    # For IFS, skip 3D variables on small level subsets in favor of extended level sets
    if model_component == "ifs":
        result = []
        level_sets = map(cmor_target.get_z_axis, target_list)
        for i in range(len(level_sets)):
            level_type, levels = level_sets[i][0], set(level_sets[i][1])
            add_to_list = True
            for level_type_other, levels_other in level_sets:
                if level_type == level_type_other and levels.issubset(set(levels_other)) \
                        and not set(levels_other).issubset(levels):
                    add_to_list = False
                    break
            if add_to_list:
                result.append(target_list[i])
        # Incompatible variables fix: zg7h and zg27
        vartabs = map(lambda t: (t.table, t.variable), result)
        if ("6hrPlevPt", "zg7h") in vartabs and ("6hrPlevPt", "zg27") in vartabs:
            result.remove([t for t in target_list if (t.table, t.variable) == ("6hrPlevPt", "zg27")][0])
        return result
    return target_list


