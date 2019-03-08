import logging


def keep_variable(target, model_component, ecearth_config):
    variable = target.variable
    table = target.table

    if variable == "tos":
        return model_component == "nemo"

    if variable in ["pfull", "zg", "ps", "tas", "ua", "va"]:
        if table.startswith("AER"):
            return model_component == "tm5"
        else:
            return model_component == "ifs"

    if variable in ["cfc12", "cfc13", "c14", "sf6"]:
        return model_component == "nemo" and ecearth_config == "CC"

    return True
