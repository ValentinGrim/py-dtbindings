"""@package py-dtbindings
@author Valentin Monnot
"""
import os
from bindings import SDTBindings

if __name__ == "__main__":
    path = "./devicetree/bindings"
    SDTBindings(path,0)
