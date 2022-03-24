"""@package py-dtbindings
@author Valentin Monnot
"""
import os
from bindings import Binding

if __name__ == "__main__":
    path = "./devicetree/bindings"
    files_dict = {}

    for dirpath, _, filenames in os.walk(path):
       if dirpath != path:
          for file in filenames:
              if ".yaml" in file:
                  files_dict.update({file.split('.')[0] : dirpath + "/" + file})

    #print(files_dict['non']) #except KeyError
    binding = []
    i = 0
    for key in sorted(files_dict):
        binding.append(Binding(files_dict[key], files_dict,1))
