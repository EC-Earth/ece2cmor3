#!/usr/bin/env python
# Thomas Reerink

# Switch the old clear sky output implementation on or off

# See the for further description the issues:
#  https://dev.ec-earth.org/issues/1237
#  https://github.com/EC-Earth/ece2cmor3/issues/772

import re
import sys
import subprocess

def main():

    error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'       # Red    error   message
    warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'       # Yellow warning message
   #error_message   = '\n Error:'                                  #        error   message
   #warning_message = '\n Warning:'                                #        warning message

    def modify(text, from_, to_):
        pattern = from_
        splitted_text = re.split(pattern,text)
        return to_.join(splitted_text)

    if len(sys.argv) == 2:
     input_file  = "../resources/ifspar.json"
    #output_file = "../resources/ifspar-old-clear-sky.json"
     output_file = "../resources/ifspar.json"

     if sys.argv[1] == "activate-old-clear-sky-output":
      subprocess.run(["git", "checkout", input_file]) 

      file = open(input_file,"r+")
      input_text = file.read()
      file.close()

      # Revert the changes in ece2cmor3/resources/ifspar.json for:
      #  rsdscs (SW downwelling radiative flux at the surface)
      #  rldscs (LW downwelling radiative flux at the surface)
      # of commit: https://github.com/EC-Earth/ece2cmor3/commit/d0a134c33d8025cf105fb576f4b208768884d28e#diff-025894a61a5ef7f02c609fcb3373f1964f55f5388bf475c7e819bcb3e81249c2

      # rsdscs (SW downwelling radiative flux at the surface)
      modified_text = modify(input_text   ,'"source": "1.126"','"source": "132.129"')
      modified_text = modify(modified_text,'"target": "rsdscs"','"target": "rsdscs",\n        "expr": "(var176<=1e-10)*var210+(var176>1e-10)*var210*var169/var176"')

      # rldscs (LW downwelling radiative flux at the surface)
      modified_text = modify(modified_text,'"source": "2.126"','"source": "104.129"')
      modified_text = modify(modified_text,'"target": "rldscs"','"target": "rldscs",\n        "expr": "var211-var177+var175"')

      with open(output_file, 'w') as file:
          file.write(modified_text)

      print('The old clear sky output is activated.')
     elif sys.argv[1] == 'deactivate-old-clear-sky-output':
      subprocess.run(["git", "checkout", input_file])
      print('The old clear sky output is deactivated.')
     else:
      print()
      print(error_message, 'The value of the first argument is wrong.')
      print()
      print(' This scripts requires one argument: There are only two options:')
      print('  ', sys.argv[0], 'activate-old-clear-sky-output')
      print('  ', sys.argv[0], 'deactivate-old-clear-sky-output')
      print()

    else:
     print()
     print(' This script needs one argument: E.g.:')
     print('  ', sys.argv[0], 'activate-old-clear-sky-output')
     print('  ', sys.argv[0], 'deactivate-old-clear-sky-output')
     print()

if __name__ == "__main__":
    main()
