# This file is used for test purspose
# It's not part of the docs
from bindings import SDTBindings
import sys

if __name__ == "__main__":
	mySDTBindings = SDTBindings(verbose = 0)
	myBinding = mySDTBindings.get_binding("st,stm32mp157-pinctrl")

	if not myBinding:
		print("Error, no binding found")
		sys.exit(-1)

	myProp = myBinding.get_prop_by_name("dcmi-sleep-1")

	if not myProp:
		print("Error, patternProperties broken")
		sys.exit(-1)
