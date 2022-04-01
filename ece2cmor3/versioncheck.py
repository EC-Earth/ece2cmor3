#!/usr/bin/env python

import argparse
import os

from ece2cmor3 import ece2cmorlib, __version__, cmor_utils

def main(args=None):

    formatter = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog='ece2cmor', max_help_position=30)

    parser = argparse.ArgumentParser(description="Post-processing and cmorization of EC-Earth output", formatter_class=formatter)
    required = parser.add_argument_group("required arguments")


    # Set your test case:
    case=2

    if case == 1:
     from setup import get_git_hash
     parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__.version + ' with sha: ' + get_git_hash())
    elif case == 2:
     from cmor_utils import get_git_hash
     parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__.version + ' with sha: ' + get_git_hash())
    elif case == 3:
     from setup import get_git_hash
     parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__.version + ' ........................................ ece2cmor_git_revision: ' + get_git_hash())
    elif case == 4:
     from cmor_utils import get_git_hash
     parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__.version + ' ........................................ ece2cmor_git_revision: ' + get_git_hash())
    elif case == 5:
     parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__.version)
    else:
     # The current ece2cmor default way:
     parser.add_argument("-V", "--version", action="version", version="%(prog)s {version}".format(version=__version__.version))

    args = parser.parse_args()

if __name__ == "__main__":
    main()
