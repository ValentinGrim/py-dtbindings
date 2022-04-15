# py-dtbindings

## Brief
  This python "lib" aim is to extract devicetree bindings informations.

## Documentation
[Doxygen on github.io](https://valentingrim.github.io/py-dtbindings/)

## TODO
- [Docs TODO Page ](https://valentingrim.github.io/py-dtbindings/todo.html)


## Class
### SDTBindings
This is the root class, this is the one that should be called.
Give it the path of your local copy of bindings and it will load it.

- It will search for every YAML file in provided dir and subdir
- It will attempt to decode it and make is own list of compatible.

As there is an internal list of compatible pointing on file its related to,
you should call get_binding method to retrieve a Binding from a given compatible  
(e.g. myBinding = mySDTBindings.get_binding("gpio-keys") will return a Binding object created from gpio-keys.yaml binding)

### Binding

This class represents a binding :)

- It will load the provided binding
- It will extract main information (e.g. id, schema, properties, required ...)
- If there is some inclusion, it will also load them and add these properties

Public Member Functions:
- get_prop_by_name(name)  
``Will return a Prop item by calling :
BindingProps.prop_from_name(name) functions``
- required()  
``Will return required properties list (str)``
- optional()  
``Will return optional properties list (str)``

Public Attributes:
- file_name
- id
- schema
- maintainers
- title
- examples

### BindingProps

This class represents the properties of a binding.
It stands to be initialized by a Binding class and access through it.
This class var will also contain binding properties of included bindings
(e.g. using "allOf/$ref")

All member functions should be called by a Binding class for initializing

## Usage
### Linux:

    sudo apt install swig python3 python3-ruamel.yaml
    pip3 install -r ./requirement.txt

Then juste add bindings.py to your project and let's go ``¯\_(ツ)_/¯`` !

## Devicetree files
wget-ed from https://www.kernel.org/doc/Documentation/devicetree/bindings/

## Contribute
Feel free to improve this as you want and share it !
Also, I'm listening to any comments !

## Third Party
- [Doxygen Awesome](https://github.com/jothepro/doxygen-awesome-css)
- [dtschema](https://github.com/devicetree-org/dt-schema)

## Contact
- Valentin Monnot <vmonnot@outlook.com>
