 # This file is used for test purspose
 # It's not part of the docs
from bindings import SDTBindings

if __name__ == "__main__":
	mySDTBindings = SDTBindings(verbose = 0)
	myBinding = mySDTBindings.get_binding("")
