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
Alternative: `python3 setup.py install`