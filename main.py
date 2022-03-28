"""@package py-dtbindings
@author Valentin Monnot
@copyright 2022 - MIT License
"""
import os
from bindings import SDTBindings

if __name__ == "__main__":
    path = "./devicetree/bindings"
    SDTBindings(path,0)
