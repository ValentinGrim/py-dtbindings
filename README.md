# py-dtbindings

## Brief
  This python "lib" aim is to extract devicetree bindings informations.

## [Documentation](https://valentingrim.github.io/py-dtbindings/)

## TODO :
		- Update this readme !
		- Complete _compat_extractor() in SDTBindings because of the rework of Prop
		- Currently mySDTBindings.get_binding("gpio-keys") doesn't work because of above point


## Class
  ### SDTBindings
    This is the root class, this is the one that should be called.
    Give it the path of your local copy of bindings and it will load it.

    1 - It will search for every YAML file in provided dir and subdir
    2 - It will attemp to decode it and make is own list of compatible.

    Use the method get_binding by providing it a compatible string
    (e.g. myBinding = mySDTBindings.get_binding("gpio-keys")
    And it will return a Binding object created from gpio-keys.yaml binging

  ### Binding ``/!\ Need a rework (see docs)``
    This class class represent a binding :)

    1 - It will load the provided binding
    2 - It will extract main information
        (e.g. id, schema, properties, required ...)
    3 - If there is some inclusion, it will also load them and add these properties

    This class has no methods (for the moment) content is planned to be accessed through internal var (theoretically "_var" is private var)

    Accessible node list:
    - id
    - schema
    - maintainers
    - title
    - properties (BindingProps class)
    - examples

  ### BindingProps ``/!\ Need a rework (see docs)``
    This class represent properties of a binding.
    It stand to be initialized by a Binding class and access through it.
    This class var will also contains binding properties of included bindings
    (e.g. using "allOf/$ref")

    This class content is planned to be access through internal var (theoretically "_var" is private var).

    Accessible node list:
    - required (str list of all required properties)
    - optional (same for opional properties)
    - prop     (A python dict containing properties meant to be access using above list item as key)

## Usage
  ### Linux:

    sudo apt install swig python3 python3-ruamel.yaml
    pip3 install -r ./requirement.txt

    Then juste add bindings.py to your project and let's go ``¯\_(ツ)_/¯`` !

## Devicetree files
wget-ed from https://www.kernel.org/doc/Documentation/devicetree/bindings/

## Contribute
  Feel free to improve this as you want and share it !
  Also I'm listening to any comments !

## Contact
  - Valentin Monnot <vmonnot@outlook.com>
