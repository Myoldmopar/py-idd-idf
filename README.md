# EnergyPlus Python IDD/IDF Utilities

Python library of EnergyPlus IDD/IDF manipulation utilities.

## Documentation

[![Documentation Status](https://readthedocs.org/projects/energyplus-idd-idf/badge/?version=latest)](https://energyplus-idd-idf.readthedocs.io/en/latest/?badge=latest)

Documentation is hosted on ReadTheDocs at https://energyplus-idd-idf.readthedocs.io/en/latest/.
To build the documentation, enter the docs/ subdirectory and execute `make html`; then open
`/docs/_build/html/index.html` to see the documentation.

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

## Installation

This package is deployed to PyPi at https://badge.fury.io/py/energyplus-idd-idf-utilities.
To install, simply `pip install energyplus-idd-idf-utilities`.
