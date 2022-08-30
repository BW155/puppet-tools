# puppet-tools
#### WARNING: This project is not complete and should be used carefully. Always check your own configuration.

## About this project
The purpose of this project is to provide a simple way to check puppet files. The original puppet linter doesn't seem to work as expected as it fails to capture missing chars from the configurations.
In addition this program also validates certain aspects of the configuration files.

## Features
- **Parsing `.pp` files of a module** (validates the syntax)
- **Validate**:
   - includes to have the corresponding classes available in the module.
   - resource references.
   - resource for valid parameter names.
   - used sources are available in the files folder of the module.

## Installation Instructions
### Pip
`pip install Puppet-Tools`

### Alternative
Clone the repository and call: `python3 -m pip install ./puppet-tools`  
or  
Call: `python3 setup.py install`


## Usage

`puppet-tools <module_directory>`  

The module should be according to the puppet standard and at least contain:
```text
module_directory
├───files
└───manifests
```

### Options
```text
  -h, --help            show this help message and exit
  -t, --print-tree      Print the tree of parsed objects
  -p, --only-parse      Only parse for format validating/linting
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Set minimum log level (Info=2, Warning=3, Error=4, Fatal=5) (default: Warning)
```
