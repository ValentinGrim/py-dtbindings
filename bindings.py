"""
@author Valentin Monnot
@copyright 2022 - MIT License
"""
import os, sys
import yaml
import re

props_key = ("oneOf", "anyOf", "allOf","const", "contains", "items", "enum")
dtschema = os.path.expanduser("~/.local/lib/python3.8/site-packages/dtschema")

class SDTBindings:
    def __init__(self,path,verbose):
        self._path = path
        self._verbose = verbose

        # Init path dict
        self._files_dict = {}
        for dirpath, _, filenames in os.walk(path):
           if dirpath != path:
              for file in filenames:
                  if ".yaml" in file:
                      self._files_dict.update({file.split('.')[0] : dirpath + "/" + file})

        # Init compatible dict
        if verbose > 2:
            print("[INFO]: Initializing compatible dict...")
        self._compat_dict = {}
        for key in self._files_dict:
            tmp = Binding(self._files_dict[key],self._files_dict,verbose)
            try:
                self._compat_extractor(key,tmp.properties.prop["compatible"])
            except KeyError:
                pass
        if verbose > 2:
            print("[INFO]: Compatible dict initialized !")

    def _compat_extractor(self, key, compat):
        global props_key
        if type(compat) is str:
            # If not vendor specific
            if not "," in compat:
                # Avoid process compat outside of it base bindings
                if not compat in key:
                    # Some compat like pwm-leds or gpio-leds are stored in
                    # a file name that is reversed
                    # e.g. pwm-leds is part of leds-pwm.yaml)
                    if "-" in compat:
                        if not "-" in key and compat.split("-")[1] == key:
                            # Add to the list
                            self._compat_dict.update({compat : self._files_dict[key]})
                        elif all(x in key.split("-") for x in compat.split("-")):
                            # Add to the list
                            self._compat_dict.update({compat : self._files_dict[key]})
                        elif key == "opp-v2": # The only one exception
                            # Add to the list
                            self._compat_dict.update({compat : self._files_dict[key]})
                        else:
                            # DO NOT add to the list
                            pass
                    else:
                        # Add to the list
                        self._compat_dict.update({compat : self._files_dict[key]})
                else:
                    # Add to the list
                    self._compat_dict.update({compat : self._files_dict[key]})
            else:
                # Add to the list
                self._compat_dict.update({compat : self._files_dict[key]})

        elif type(compat) is dict:
            for _key,value in compat.items():
                if _key in props_key:
                    self._compat_extractor(key,value)
        elif type(compat) is list:
            pass
        else:
            # We should never ever be there.
            print("[ERR ]: Unknown compatible type", type(compat))
            print(self._files_dict[key])
            sys.exit(-1)

    def get_binding(self, compatible):
        return return Binding(self._compat_dict[compatible],self._files_dict,self._verbose)

class Binding:
    def __init__(self, path, files_dict,verbose):
        self._verbose = verbose
        self._path = path.rsplit('/',1)[0]
        self._files_dict = files_dict
        self.file_name = path.rsplit('/',1)[1]

        global dtschema

        try:
            self._file = open(path, 'r')
        except OSError:
            print('[ERR ]: Cannot open', path)
            print("[INFO]: If you didn't called this file, check that $ref is correctly set")
            sys.exit(-1)

        self._content = yaml.load(self._file, Loader=yaml.FullLoader)

        # Loading basics information
        self.id = self._content['$id'].replace('#','')
        self.schema = self._content['$schema'].replace('#','')
        self.maintainers = self._content['maintainers']
        self.title = self._content['title']

        # Init allOf and load $ref bindings if exist
        self._refs = []
        self._if = []
        try:
            for item in self._content['allOf']:
                if '$ref' in item:
                    path = ""

                    if "schemas/" in item['$ref']:
                        #TODO:  Instead of spliting on '#', we should be able
                        #       to handle the case where there node ref
                        #       after this '#'. (If it make sens)
                        path = dtschema + item['$ref'].split('#')[0]
                    elif "../" in item['$ref']:
                        path = self._path.rsplit('/',1)[0] + item['$ref'].replace('..','').replace('#','')
                    else:
                        if "/common.yaml" in item['$ref']:
                            if not "../" in item['$ref']:
                                path = self._path
                                while path.rsplit('/',1)[1] != "bindings":
                                    path = path.rsplit('/',1)[0]
                                path += '/' + item['$ref'].split('#')[0]
                        else:
                            #TODO:  Same as above
                            name = item['$ref'].split('#')[0].replace('.yaml','')
                            name = name.rsplit('/',1)[0]
                            path = self._files_dict[name]

                    if self._verbose > 2:
                        print("[INFO]: Binding <%s> loading $ref <%s>" % (self.file_name, path))

                    self._refs.append(Binding(path,self._files_dict,self._verbose))
                if 'if' in item:
                    self._if.append(item)
        except KeyError:
            if verbose > 2:
                print("[INFO]: No node 'allOf' found for", self.file_name)
            pass

        try:
            self._required = self._content['required']
        except KeyError:
            if verbose > 1:
                print("[WARN]: No node 'required' found for ", self.file_name)
            self._required = False

        try:
            self.properties = BindingProps(self._content['properties'], self._required)
        except KeyError:
            self.properties = BindingProps({},[])
            if verbose:
                print("[WARN]: No node 'properties' found for ", self.file_name)
        # If $ref, load bindings from subclass
        for binding in self._refs:
            self.properties.add_from_BindingProp(binding.properties)


        try:
            self.examples = self._content['examples']
        except KeyError:
            if verbose > 2:
                print("[INFO]: No examples found for ", self.file_name)

class BindingProps:
    def __init__(self, prop, required):
        self.prop = prop
        self._list = []

        for key in self.prop:
            self._list.append(key)
        self._list.sort()

        self.required = []
        self.optional = []
        self._update(required)

    def add_from_BindingProp(self,prop):
        self.required += prop.required
        self._list += prop._list
        # Remove duplicates
        self._list = list(dict.fromkeys(self._list))
        # Update
        self.prop.update(prop.prop)
        self._update()


    def _update(self,required=False):
        if required:
                self.required = required
                self.optional = [item for item in self._list if item not in required]
        else:
            if self.required:
                self.optional = [item for item in self._list if item not in self.required]
            else:
                self.optional = [item for item in self._list]
