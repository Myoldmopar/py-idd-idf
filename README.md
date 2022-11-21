# EnergyPlus Python IDD/IDF Utilities

Python library of EnergyPlus IDD/IDF manipulation utilities.

## Documentation

[![Documentation Status](https://readthedocs.org/projects/energyplus-idd-idf/badge/?version=latest)](https://energyplus-idd-idf.readthedocs.io/en/latest/?badge=latest)

Documentation is hosted on ReadTheDocs at https://energyplus-idd-idf.readthedocs.io/en/latest/.
To build the documentation, enter the docs/ subdirectory and execute `make html`; then open
`/docs/_build/html/index.html` to see the documentation.

## Installation

This package is deployed to PyPi at https://badge.fury.io/py/energyplus-idd-idf-utilities.
To install, simply `pip install energyplus-idd-idf-utilities`.

## Basic Usage

Once installed, the utilities are available for use as a library of functionality to call from Python, or with a very limited (for now) CLI called `energyplus_idd_idf`.
Some example CLI calls:

Get the CLI form:

```shell
$ ./some_python_venv/bin/energyplus_idd_idf --help
usage: energyplus_idd_idf [-h] [--idd_check] [--idd_obj_matches IDD_OBJ_MATCHES] [--summarize_idd_object SUMMARIZE_IDD_OBJECT] filename

EnergyPlus IDD/IDF Utility Command Line

positional arguments:
  filename              Path to IDD/IDF file to be operated upon

optional arguments:
  -h, --help            show this help message and exit
  --idd_check           Process the given IDD file and report statistics and issues
  --idd_obj_matches IDD_OBJ_MATCHES
                        Find IDD objects that match the given basic pattern
  --summarize_idd_object SUMMARIZE_IDD_OBJECT
                        Print a summary of a single IDD object by name

This CLI is in infancy and will probably have features added over time

```

Check an existing IDD file and get basic information:

```shell
$ ./some_python_venv/bin/energyplus_idd_idf --idd_check /path/to/EnergyPlus-22-2-0/Energy+.idd 
{
  "message": "Everything looks OK",
  "content": {
    "idd_version": "22.2.0",
    "idd_build_id": "c249759bad",
    "num_groups": 59,
    "num_objects": 881
  }
}

```

Find all objects which match a certain name pattern:

```shell
$ ./some_python_venv/bin/energyplus_idd_idf --idd_obj_matches 'Coil:Cooling*' /path/to/EnergyPlus-22-2-0/Energy+.idd 
{
  "message": "Everything looks OK",
  "content": {
    "pattern": "Coil:Cooling*",
    "matching_objects": [
      "Coil:Cooling:Water",
      "Coil:Cooling:Water:DetailedGeometry",
      "Coil:Cooling:DX",
      "Coil:Cooling:DX:CurveFit:Performance",
      "Coil:Cooling:DX:CurveFit:OperatingMode",
      "Coil:Cooling:DX:CurveFit:Speed",
      "Coil:Cooling:DX:SingleSpeed",
      "Coil:Cooling:DX:TwoSpeed",
      "Coil:Cooling:DX:MultiSpeed",
      "Coil:Cooling:DX:VariableSpeed",
      "Coil:Cooling:DX:TwoStageWithHumidityControlMode",
      "Coil:Cooling:DX:VariableRefrigerantFlow",
      "Coil:Cooling:DX:VariableRefrigerantFlow:FluidTemperatureControl",
      "Coil:Cooling:WaterToAirHeatPump:ParameterEstimation",
      "Coil:Cooling:WaterToAirHeatPump:EquationFit",
      "Coil:Cooling:WaterToAirHeatPump:VariableSpeedEquationFit",
      "Coil:Cooling:DX:SingleSpeed:ThermalStorage"
    ]
  }
}

```

Get specific details about a single object by name:

```shell
$ ./some_python_venv/bin/energyplus_idd_idf /path/to/EnergyPlus-22-2-0/Energy+.idd --summarize_idd_object "Coil:Cooling:DX"
{
  "message": "Everything looks OK",
  "content": {
    "searched_object_name": "COIL:COOLING:DX",
    "field": [
      "A1 : Name",
      "A2 : Evaporator Inlet Node Name",
      "A3 : Evaporator Outlet Node Name",
      "A4 : Availability Schedule Name",
      "A5 : Condenser Zone Name",
      "A6 : Condenser Inlet Node Name",
      "A7 : Condenser Outlet Node Name",
      "A8 : Performance Object Name",
      "A9 : Condensate Collection Water Storage Tank Name",
      "A10 : Evaporative Condenser Supply Water Storage Tank Name"
    ]
  }
}
```

## Testing

[![Flake8](https://github.com/Myoldmopar/py-idd-idf/actions/workflows/flake8.yml/badge.svg)](https://github.com/Myoldmopar/py-idd-idf/actions/workflows/flake8.yml)
[![Run Tests](https://github.com/Myoldmopar/py-idd-idf/actions/workflows/test.yml/badge.svg)](https://github.com/Myoldmopar/py-idd-idf/actions/workflows/test.yml)

The source is tested using the python unittest framework. 
To execute all the unit tests, simply run `nosetests` from the project root.
The tests are also executed by GitHub Actions for each commit.

## Test Coverage

[![Coverage Status](https://coveralls.io/repos/github/Myoldmopar/py-idd-idf/badge.svg?branch=master)](https://coveralls.io/github/Myoldmopar/py-idd-idf?branch=master)

Coverage of the code from unit testing is reported to Coveralls at https://coveralls.io/github/Myoldmopar/py-idd-idf.
Anything less than 100% coverage will be frowned upon. :)
