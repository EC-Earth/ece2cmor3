#!/usr/bin/env python

import argparse
import logging
import json

from ece2cmor3 import ece2cmorlib, components, taskloader

# Logging configuration
logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Create component-specified varlist json for given data request")
    parser.add_argument("--drq", metavar="FILE", type=str, required=True,
                        help="File (xlsx|json) containing requested cmor variables (Required)")
    parser.add_argument("--ececonf", metavar="COMP1,COMP2,...", type=str, required=True,
                        help="EC-Earth configuration, as comma-separated list of components (Required)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(tabledir=args.tabdir, tableprefix=args.tabid)

    # Load all variables as task targets:
    config_components = args.ececonf.split(',')
    active_components = {component: False for component in components.models}
    for component in config_components:
        if component in active_components:
            active_components[component] = True
        else:
            log.warning("EC-Earth component %s has not been recognized and will be ignored" % component)
    taskloader.load_targets(args.drq, active_components=active_components)
    result = {}
    for task in ece2cmorlib.tasks:
        component, table, variable = task.source.model_component(), task.target.table, task.target.variable
        if component in result:
            if table in result[component]:
                result[component][table].append(variable)
            else:
                result[component][table] = [variable]
        else:
            result[component] = {table: [variable]}
    with open("varlist.json", 'w') as ofile:
        json.dump(result, ofile, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main()
