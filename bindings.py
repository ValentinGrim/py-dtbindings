##
#	@file		bindings.py
#	@author		Valentin Monnot
#	@copyright 	SPDX-License-Identifier: MIT
#	@version	v1.3.0
#	@date 		2022

import os, sys
import yaml
import re

from typing import NamedTuple, Any

##
#	@var		dtschema
#	@brief		Path to dtschema python library in order to access schemas
dtschema = "./download/dtschema"

##
#	@var		nodes_types
#	@brief		This dict is used to store node type information for
#			"standard" and static properties
nodes_types = dict()

##
#	@var 		dtschema_types
#	@brief		This dict contains an exhaustive list of all dt types as key
#			where value is the C equivalent
#	@details	These types are comming from dtschema/type.yaml
#
dtschema_types = {	"flag"				: "bool",
			"boolean"			: "bool",
			"cell"				: "uint32_t",
			"string"			: "char *",
			"non-unique-string-array" 	: "char **",
			"string-array"			: "char **",
			"uint8-item"			: "uint8_t",
			"uint8" 			: "uint8_t",
			"uint8-array" 			: "uint8_t *",
			"uint8-matrix"			: "uint8_t **",
			"int8-item" 			: "int8_t",
			"int8"				: "int8_t",
			"int8-array"			: "int8_t *",
			"int8-matrix"			: "int8_t **",
			"uint16-item" 			: "uint16_t",
			"uint16"			: "uint16_t",
			"uint16-array"			: "uint16_t *",
			"uint16-matrix" 		: "uint16_t **",
			"int16-item" 			: "int16_t",
			"int16" 			: "int16_t",
			"int16-array" 			: "int16_t *",
			"int16-matrix" 			: "int16_t **",
			"uint32-item"			: "uint32_t",
			"uint32"			: "uint32_t",
			"uint32-array"			: "uint32_t *",
			"uint32-matrix" 		: "uint32_t **",
			"int32-item"			: "int32_t",
			"int32"				: "int32_t",
			"int32-array"			: "int32_t *",
			"int32-matrix"			: "int32_t **",
			"uint64"			: "uint64_t",
			"uint64-array"			: "uint64_t *",
			"uint64-matrix" 		: "uint64_t **",
			"int64-item"			: "int64_t",
			"int64"				: "int64_t",
			"int64-array"			: "int64_t *",
			"int64-matrix"			: "int64_t **",
			"phandle"			: "void *",
			"phandle-array"			: "void *",
			"object"			: "void *"}

##
#	@class		SDTBindings
#	@brief		The main class that you should call
#	~~~~~~~~~~~~~~~~~~~~~
#	# This exemple will print required for i2c-mux-pinctrl
#	from bindings import SDTBindings
#	if __name__ == "__main__":
#		myPath = "./devicetree/bindings"
#		mySDT = SDTBindings(myPath,0)
#
#		# Retrieve a Binding() by its name
#		myBinding = mySDT.get_binding("i2c-mux-pinctrl")
#
#		print(myBinding.required())
#	~~~~~~~~~~~~~~~~~~~~~
class SDTBindings:
	def __init__(self,path = "./download/bindings", verbose = 0,test = False):
		##
		#	@var		_path
		#	@brief		Internal reference to rootdir of bindings
		self._path 		= path
		##
		#	@var		_verbose
		#	@brief		Internal reference for printing debug level (0 to 3)
		self._verbose 		= verbose
		##
		#	@varDuplicated	_files_dict
		#	@brief		Internal dict where key are filename without extension (e.g. serial)\n
		#			value are complet path to these file
		self._files_dict 	= dict()
		##
		#	@var		_compat_dict
		#	@brief		Internal reference similar to #_files_dict but keys are 'compatible'
		self._compat_dict	= dict()

		# Download kernel.org dtbindings
		if not os.path.exists(self._path):
			print("No local bindings found, downloading them from kernel.org")
			print("This may take up to 5 minutes...")
			if self._verbose:
				os.system("wget -r -A *.yaml --no-parent --cut-dirs=3 -nH -P download https://www.kernel.org/doc/Documentation/devicetree/bindings/")
			else:
				os.system("wget -r -A *.yaml --no-parent --cut-dirs=3 -nH -P download -q https://www.kernel.org/doc/Documentation/devicetree/bindings/")
			print("Bindings download done !")

		# Download devicetree.org dtschema
		if not os.path.exists(dtschema):
			print("No local dtschema found, downloading them from github.com/devicetree-org/dt-schema")
			print("This may take up to a minute...")

			os.system("wget -P download/tmp -q https://github.com/devicetree-org/dt-schema/archive/refs/heads/main.zip")
			os.system("unzip download/tmp/main.zip -d download/tmp/ > download.log")
			os.system("cp -r download/tmp/dt-schema-main/dtschema/ download >> download.log")
			os.system("rm -r download/tmp >> download.log")
			os.system("rm download/dtschema/*.py >> download.log")
			os.system("rm download/dtschema/.gitignore >> download.log")

			print("Dt-schema download done !")


		for dirpath, _, filenames in os.walk(self._path):
			if dirpath != self._path:
				for file in filenames:
					if ".yaml" in file:
						self._files_dict.update({file.split('.')[0] : dirpath + "/" + file})

		_init_dtschema_list(verbose)

		# Init compatible dict

		if verbose > 2:
			print("[INFO]: Initializing compatible dict...")

		for key in self._files_dict:
			tmp = Binding(self._files_dict[key],self._files_dict,verbose)
			tmp = tmp.get_prop_by_name("compatible")
			if tmp:
				self._compat_extractor(key,tmp.value)
			else:
				pass

		if test:
			file_t = open('test.txt','w')
			origin = sys.stdout
			sys.stdout = file_t

			for compat in self._compat_dict.items():
				if self._verbose:
					print(compat)
				else:
					if not ',' in compat[0]:
						print(compat)

			file_t.close()
			sys.stdout = origin

		if verbose > 2:
			print("[INFO]: Compatible dict initialized !")

	##
	#	@fn		_compat_extractor(self, key, compat)
	#	@brief		Extract compatible node from properties and
	#			init a dict like #_files_dict to access path through compatible
	#	@todo		Process compatible with "pattern"\n
	#			Process "snps,dwmac"
	def _compat_extractor(self, key, compat):
		# TODO: ???
		if key == 'snps,dwmac':
			return

		if isinstance(compat, Prop):
			if compat.name == 'const':
				self._duplicate_checker(compat.value,key)

			elif compat.name == 'enum':
				for item in compat.value:
					self._duplicate_checker(item, key)

			elif compat.name in ('contains','items','oneOf','allOf','anyOf'):
				self._compat_extractor(key,compat.value)

			elif compat.name == "pattern":
				# TODO
				pass

			else:
				# Description and deprecated, ignore it
				pass
		else:
			if type(compat) is str:
				self._duplicate_checker(compat, key)
			if type(compat) == list:
				for item in compat:
					self._compat_extractor(key, item)
	##
	#	@fn		get_binding(self, compatible)
	#	@brief		Init the Binding class corresponding to compatible param
	#	@param		compatible	The compatible you want the binding for
	def get_binding(self, compatible):
		try:
			return Binding(self._compat_dict[compatible],self._files_dict,self._verbose)
		except KeyError:
			return None

	##
	#	@fn		_duplicate_checker(self, item, key)
	#	@brief		Used by _compat_extractor() in order to check if compatible
	#			have duplicate
	def _duplicate_checker(self, item, key):
		try:
			# Check if already exist in the list and if path are diff
			if self._compat_dict[item] != self._files_dict[key]:
				# Check last modif to choose which one we keep
				if not item in key and not key in item:
					if ',' in item:
						if os.stat(self._compat_dict[item]).st_mtime > os.stat(self._files_dict[key]).st_mtime:
							if self._verbose:
								print("[WARN]: Not added '" + item + "' in " + self._files_dict[key])
								print("[WARN]: Item already exist in " + self._compat_dict[item])
							return
					else:
						if self._verbose:
							print("[WARN]: Not added '" + item + "' in " + self._files_dict[key])
							print("[WARN]: Item already exist in " + self._compat_dict[item])
							print("[INFO]: Existing item might be wrong and will be replace later...")
						return
		except KeyError:
			pass

		if not ',' in item:
			# Avoid process compat outside of it base binding
			if not item in key and not key in item:
				# Some compat like pwm-leds or gpio-leds are stored in
				# a file name that is reversed
				# e.g. pwm-leds is part of leds-pwm.yaml)
				if '-' in item:
					if not "-" in key and item.split("-")[1] == key:
						# Add to the list
						self._compat_dict.update({item : self._files_dict[key]})
					elif any(x in key.split("-") for x in item.split("-")):
						# Add to the list
						# simple-bus is a schema and can be added to this list
						# by fsl,spba-bus.yaml but, it shouldn't be in this list
						# since this list doesn't contains schemas
						if not item == "simple-bus":
							self._compat_dict.update({item : self._files_dict[key]})
					elif key == "opp-v2": # The only one exception
						# Add to the list
						self._compat_dict.update({item : self._files_dict[key]})
					else:
						# simple-mfd had no yaml
						if not item == "simple-mfd":
							self._compat_dict.update({item : self._files_dict[key]})
				else:
					# Add to the list
					self._compat_dict.update({item : self._files_dict[key]})
			else:
				# Add to the list
				self._compat_dict.update({item : self._files_dict[key]})
		else:
			# Add to the list
			self._compat_dict.update({item : self._files_dict[key]})

##
#	@class		Binding
#	@brief		This class represent a binding document
class Binding:
	def __init__(self, path, files_dict,verbose):
		##
		#	@var	_verbose
		#		Internal reference for printing debug level (0 to 3)
		self._verbose 	= verbose
		##
		#	@var	_path
		#		Internal reference for path of the main file
		self._path	= path.rsplit('/',1)[0]
		##
		#	@var	_files_dict
		#		Internal reference on all YAML path in root dir. Given by SDTBindings
		self._files_dict = files_dict
		##
		#	@var	_content
		#		Internal pointer on loaded yaml
		self._content	= None
		##
		#	@var	_file
		#		Internal file pointer
		self._file	 = None
		##
		#	@var	_refs
		#		Internal reference on Binding included by $ref in allOf node
		self._refs 	= list()
		##
		#	@var	_if
		#		Internal reference on if node from allOf node (currently unused)
		self._if 	= list()
		##
		#	@var	_props
		#		Internal reference on BindingProps containing properties information
		self._props 	= BindingProps(verbose)
		##
		#	@var	file_name
		#		The YAML file name represented by this class
		self.file_name	= path.rsplit('/',1)[1]
		##
		#	@var	id
		#		Usually kernel.org link to this binding
		self.id		= str()
		##
		#	@var	schema
		#		dt-schema used as base for this binding
		self.schema	= str()
		##
		#	@var	maintainers
		#		Maintainers of this bindings
		self.maintainers= str()
		##
		#	@var	title
		#		Title of this bindings
		self.title	= str()
		##
		#	@var	examples
		#		If maintainers did some, you can find dts node examples here
		self.examples	= str()

		global dtschema

		try:
			self._file = open(path, 'r')
		except OSError:
			if verbose:
				print("[ERR ]: Cannot open", path)
				print("	A $ref property might have a wrong path")
				print("	For more information, please use debug lvl 3")
			return None

		self._content = yaml.safe_load(self._file)

		# Loading basics information
		self.id = self._content['$id'].replace('#','')
		self.schema = self._content['$schema'].replace('#','')
		self.maintainers = self._content['maintainers']
		self.title = self._content['title']

		# Initializing allOf node and properties
		self._init_allOf()
		self._init_Properties()

		try:
			self.examples = self._content['examples']
		except KeyError:
			if verbose > 2:
				print("[INFO]: No examples found for ", self.file_name)

	##
	#	@fn		_init_allOf(self)
	#	@brief		Init #_refs
	def _init_allOf(self):
		try:
			self._content['allOf']
		except KeyError:
			if self._verbose > 2:
				print("[INFO]: No node 'allOf' found for", self.file_name)
			return

		for item in self._content['allOf']:
			if '$ref' in item:
				path = str()
				# If ref pointing on a dt-schema, path used is defined
				# at top of this script and point on path where pip3
				# installed dt-schema
				if "schemas/" in item['$ref']:
					#TODO:  Instead of spliting on '#', we should be able
					#       to handle the case where there node ref
					#       after this '#'. (If it make sens)
					path = dtschema + item['$ref'].split('#')[0]

					# Relative path
				elif "../" in item['$ref']:
					path = self._path.rsplit('/',1)[0] + item['$ref'].replace('..','').replace('#','')
				else:
					# There is multiple common.yaml.
					# Some of them have relative path and can be process
					# with the above statement, other generally are
					# stored in other dir
					# e.g. root_dir/dir_a/subdir_a/myfile.yaml
					#   _______________________________|
					#  |-> root_dir/dir_b/common.yaml
					if "/common.yaml" in item['$ref']:
						path = self._path
						# This loop is used to get back to root dir
						while path.rsplit('/',1)[1] != "bindings":
							path = path.rsplit('/',1)[0]
						path += '/' + item['$ref'].split('#')[0]
					# Finaly, normal ref
					else:
						#TODO:  Same as above
						name = item['$ref'].split('#')[0].replace('.yaml','')

						if '/' in name:
							name = name.rsplit('/',1)[1]

						try:
							path = self._files_dict[name]
						except KeyError:
							path = None
							if self._verbose:
								print("[WARN]: <%s> not found for <%s>. Is path correct ?" % (item['$ref'].split('#')[0], self.file_name))

				if path:
					if self._verbose > 2:
						print("[INFO]: Binding <%s> loading $ref <%s>" % (self._path + "/" + self.file_name, path))
					self._refs.append(Binding(path,self._files_dict,self._verbose))

			if 'if' in item:
				self._if.append(item)

	##
	#	@fn		_init_Properties(self)
	#	@brief		Init #_props which is basically a BindingProps item
	#	@details	Exctract required list from #_content and call
	#			BindingProps.add_required() function
	def _init_Properties(self):
		# Extract required node
		if self._verbose > 2:
			print("[INFO]: Initializing properties for", self.file_name)

		try:
			required = self._content['required']
		except KeyError:
			if self._verbose > 1:
				print("[WARN]: No node 'required' found for", self.file_name)
			required = False
		self._props.add_required(required)

		# Exctract properties node
		try:
			properties = self._content['properties']
		except KeyError:
			if self._verbose:
				print("[WARN]: No node 'properties' found for", self.file_name)
			properties = False
		self._props.add_properties(properties)

		# Extract patternProp node
		try:
			patternProp = self._content['patternProperties']
		except KeyError:
			if self._verbose > 1:
				print("[WARN]: No node 'patternProperties' found for", self.file_name)
			patternProp = False
		self._props.add_properties(patternProp)

		# Add ref properties
		for binding in self._refs:
			self._props.add_from_BindingProp(binding._props)

		if self._verbose > 2:
			print("[INFO]: Properties initialized for ", self.file_name)

	##
	#	@fn		get_prop_by_name(self, name)
	#	@brief		The clean way to retrieve a property from BindingProps
	#	@param		name	Name of the desired props
	#	@return		A Prop item or None
	def get_prop_by_name(self, name):
		return self._props.prop_from_name(name)

	##
	#	@fn		required(self)
	#	@brief		The clean way to retrieve BindingProps._required
	#	@return		BindingProps._required
	def required(self):
		return self._props._required

	##
	#	@fn		optional(self)
	#	@brief		The clean way to retrieve BindingProps._optional
	#	@return		BindingProps._optional
	def optional(self):
		return self._props._optional

##
#	@class 		Prop
#	@brief		This NamedTuple represent a single property and its value(s)
#	@details	As NamedTuple var can't be detected by doxygen, here it's how it work:\n
#			Prop is like a C struct, with 2 field:\n
#				* Prop.name 	-> The name of the property\n
#				* Prop.value 	-> Value(s) of the property
class Prop(NamedTuple):
	name: str
	value: Any

##
#	@class 		MainProp
#	@brief		This NamedTuple represent a single property and its value(s)
#	@details	This class is like Prop but should be at top level (as Prop.value could be another Prop)\n
#			As NamedTuple var can't be detected by doxygen, here it's how it work:\n
#			MainProp is like a C struct, with 3 field:\n
#				* MainProp.name 	-> The name of the property\n
#				* MainProp.value 	-> Value(s) of the property\n
#				* MainProp.type		-> Type of the property
class MainProp(NamedTuple):
	name: str
	value: Any
	type: Any

	def __contains__(self, item):
		if not isinstance(item, str):
			return False
		return self._contains_finder(item, self.value)

	def __getitem__(self, key):
		if not isinstance(key, str):
			return None
		return self._getitem_finder(key, self.value)

	##
	#	@fn		_contains_finder(self, name, val)
	#	@brief		Recursive private method used by magic method `__contains__()`
	#			to find if given item is in.
	def _contains_finder(self, name, val):
		if isinstance(val, Prop):
			if val.name == name:
				return True
			else:
				return self._contains_finder(name, val.value)

		elif type(val) == list:
			for item in val:
				bool_t = self._contains_finder(name, item)
				if bool_t:
					return True
			return False
		return False

	##
	#	@fn		_getitem_finder(self, name, val)
	#	@brief		Recursive private method used by magic method `__getitem__()`
	#				to return Prop if given Prop.name exist.
	def _getitem_finder(self, name, val):
		if isinstance(val, Prop):
			if val.name == name:
				return val
			else:
				return self._getitem_finder(name, val.value)

		elif type(val) == list:
			for item in val:
				prop_t = self._getitem_finder(name, item)
				if prop_t:
					return prop_t
			return None
		return None


##
#	@class		BindingProps
#	@brief		This class represent the binding properties of a Binding class
#	@todo		Different algorithm could be rework as they could be more
#			clean and efficient since we had __contains__ and __getitem__ to MainProp
class BindingProps:
	def __init__(self, verbose):
		##
		#	@var	_props
		#		A dict Contains properties formatted with Prop
		self._props	= dict()
		##
		#	@var	_required
		#		A list of all required properties
		self._required 	= list()
		##
		#	@var	_optional
		#		A list of all optional properties
		self._optional 	= list()
		##
		#	@var	_verbose
		#		Internal reference for printing debug level (0 to 3)
		self._verbose 	= verbose

	##
	#	@fn		add_required(self, required)
	#	@brief		Init or update #_required
	#	@param		required	A list usually extracted from \link Binding._content \endlink
	def add_required(self, required):
		if not required:
			return
		# Init or update required list
		self._required += required
		# Remove duplicates
		self._required = list(dict.fromkeys(self._required))
		self._required.sort()
		self._update()

	##
	#	@fn		add_properties(self, properties)
	#	@brief		Init or update #_optional and _props
	#	@param		properties	A dict usually extracted from \link Binding._content \endlink
	def add_properties(self, properties):
		if not properties:
			return

		# Init or update optional list from properties
		for key in properties:
			self._optional.append(key)
		self._optional.sort()
		self._update()

		# Init or update props list from properties
		for key,item in properties.items():
			value = self._value_analyzer(item)
			type_t = self._get_type(key, item)
			self._props.update({key : MainProp(key,value,type_t)})

	##
	#	@fn		add_from_BindingProp(self, prop)
	#	@brief		This function meant to be called to add properties of a
	#			$ref binding to the main Binding
	def add_from_BindingProp(self, prop):
		self._required += prop._required
		# Remove duplicates
		self._required = list(dict.fromkeys(self._required))

		self._optional += prop._optional
		# Remove duplicates
		self._optional = list(dict.fromkeys(self._optional))
		# Update

		if 'compatible' in prop._props.keys():
			del prop._props['compatible']

		for k,v in prop._props.items():
			if not k in self._props.keys():
				self._props.update({k : v})

		self._update()

	##
	#	@fn		prop_from_name(self, name)
	#	@brief		Explicit : return a Prop for a given name
	#	@param		name	Name of the desired Prop
	#	@return		A Prop item or None
	def prop_from_name(self, name):
		try:
			return self._props[name.split('@')[0]]
		except KeyError:
			# Check if there is any pattern in nodes matching the name
			for key,value in self._props.items():
				if re.match(key, name):
					return self._props[key]

				elif type(value.value) == list:
					for prop in value.value:
						if isinstance(prop, Prop):
							if prop.name == 'pattern':
								if re.match(prop.value, name.split('@')[0]):
									return self._props[key]
		# Else return nothing
		return None

	##
	#	@fn		_update(self)
	#	@brief		Did some cleaning on #_optional list after update
	#	@details	After adding new elements to #_optional, check if these
	#			elements can be found in #_required, and so, remove them
	#			from #_optional
	def _update(self):
		if self._required:
			self._optional = [item for item in self._optional if item not in self._required]

	##
	#	@fn		_value_analyzer(self, item)
	#	@brief		Analyze value type of input and process it
	#	@details	It should be called for extract necessary info for #_props
	#			It ceate some Prop or list of Prop or simply return a var
	#			that should be added to the main Prop value
	def _value_analyzer(self, item):
		if type(item) == dict:
			# Only one item so don't need to create a list of item
			if len(item) == 1:
				key = list(item.keys())[0]
				value = list(item.values())[0]

				if type(value) in (dict,list):
					# Recurs
					return Prop(key,self._value_analyzer(value))
				return Prop(key,value)

			# More than one item so we will return a list of item
			else:
				tmp = list()
				for key, value in item.items():
					if type(value) in (dict,list):
						#Recurs so we have a list of Prop() in value and not a dict
						tmp.append(self._value_analyzer(value))
					else:
						# main Prop.value will be a list of Prop
						tmp.append(Prop(key,value))
				return tmp

		elif type(item) == list:
			tmp = list()
			for value in item:
				if type(value) in (dict,list) :
					#Recurs so we have a list of Prop() in value and not a dict
					tmp.append(self._value_analyzer(value))
				else:
					# List of literal return it and it will be part of Prop.value
					tmp.append(value)
			return tmp

		else:
			# Return literal, it will be the Prop.value
			return item

	##
	#	@fn		_get_type(self, key, item)
	#	@brief		Called by add_properties() to retrieve MainProp type
	#	@todo		All case not or partially process (see TODO:):
	#				- Item dict with '$ref' that is not schema and no 'type'\n
	#				- Item dict with '$ref' that's not part of bindings.dtschema_types dict\n
	#				- Item that doesn't fit in any if else
	def _get_type(self, key, item):
		if key in nodes_types.keys():
			return nodes_types[key]
		else:
			if isinstance(item, dict):
				if '$ref' in item.keys():
					# A type has been given by the vendor, nice job !
					ref = item['$ref']

					if '/schemas/' in ref:
						try:
							return dtschema_types[ref.rsplit('/',1)[1]]
						except KeyError:
							# TODO: Maybe ? idk if graph is usefull for TF-M ?
							if self._verbose > 1:
								print("[WARN]: Unknown type %s for %s, set it to unknown" % (ref.rsplit('/',1)[1],key))
							return 'unknown'
					else:
						if not 'type' in item.keys():
							# TODO: Here there is some 'phy', 'phy-device' or 'mdio'
							# Idk what to do with that
							return 'unknown'
						else:
							return item['type']

				elif 'type' in item.keys():
					# A type has been given by the vendor, nice job !
					type_t = item['type']
					if type_t == "object":
						return "object"
					elif type_t == "boolean":
						return "bool"
					else:
						# for what i know, there is no way we fall here
						print("[WARN]: Unconventional type %s for %s" % (type,key))
						return "unknown"
				else:
					if not '#' in key:
						# Usually give name of member for a given array
						# e.g reg and reg-name work together
						# We might use reg-name to name C var of all reg member
						# beside of a single reg array
						if "name" in key:
							return "name"
						else:
							# Vendor should give a type for each nodes that not's
							# part of dtschema, so rip.
							return "unknown"
					else:
						# Idk which type give to #****-**** properties
						# As they wont be in the output, they are "fixed"
						# And they usually describe a number of cells
						# Admit their none so we might be able to retrieve these
						# ez if needed
						return "none"

			if '#' in key:
				return 'none'
			# TODO: Else all ???
			return "unknown"

##
#	@fn		_init_dtschema_list()
#	@brief		Init a list of type from dtschemas
#	@details	This fct is called by SDTBindings __init__()
#			It will load every YAML in dtschema python lib and update
#			#nodes_types dict with the ones given by dtschemas
def _init_dtschema_list(verbose):
	files_dict = dict()

	for dirpath, _, filenames in os.walk(dtschema):
		if dirpath != dtschema and not "meta-schemas" in dirpath:
			for file in filenames:
				if ".yaml" in file:
					files_dict.update({file.split('.')[0] : dirpath + "/" + file})

	types_dict = dict()

	for _, path in files_dict.items():
		if 'graph.yaml' in path:
			continue
		try:
			file_t = open(path,'r')
		except OSError:
			if verbose:
				print("[ERR ]:  Cannot open", path)
				print("	A $ref property might have a wrong path")
				print("	For more information, please use debug lvl 3")
			continue

		yaml_t = yaml.safe_load(file_t)

		if 'properties' in yaml_t.keys():
			props_t = yaml_t['properties']
			for key,value in props_t.items():
				if key in nodes_types.keys():
					continue
				if isinstance(value,dict):
					name = [name for name in ('anyOf','oneOf') if name in value.keys()]
					if '$ref' in value.keys():
						try:
							type_t = value["$ref"].rsplit('/',1)[1]
						except IndexError:
							if value["$ref"] == "#":
								type_t = 'phandle'
							else:
								print(value)
								sys.exit(-1)
						types_dict.update({key : dtschema_types[type_t]})
					elif name:
						list_t = list()
						for item in value[name[0]]:
							if '$ref' in item.keys():
								list_t.append(dtschema_types[item['$ref'].rsplit('/',1)[1]])
							elif 'type' in item.keys():
								list_t.append(dtschema_types[item['type']])
						if len(list_t) == 1:
							types_dict.update({key : list_t[0]})
						else:
							# e.g. (object, phandle) return (void *, void *)
							if list_t[0] == list_t[1]:
								types_dict.update({key : list_t[0]})
							else:
								types_dict.update({key : tuple(list_t)})
					else:
						pass
						#print(value)

		nodes_types.update(types_dict)
