EnergyPlus Python IDD/IDF Utilities
===================================

Python library of EnergyPlus IDD/IDF manipulation utilities.

Documentation |image0|
----------------------

Documentation (just skeleton for now) is hosted on
`ReadTheDocs <http://python-iddidf-library-for-energyplus.readthedocs.io/en/latest/?badge=latest>`__.
To build the documentation, enter the docs/ subdirectory and execute ``make html``; then open
``/docs/_build/html/index.html`` to see the documentation.

Testing |image1|
----------------

The source is tested using the python unittest framework. To execute all
the unit tests, nose is utilized by the setup script (execute via `python setup.py test``. The tests are also
executed by `Travis CI <https://travis-ci.org/Myoldmopar/py-idd-idf>`__ for each commit.

Test Coverage |CoverageStatus|
------------------------------

Coverage of the code from unit testing is reported by
`Travis <https://travis-ci.org/Myoldmopar/py-idd-idf>`__ to
`Coveralls <https://coveralls.io/github/Myoldmopar/py-idd-idf?branch=master>`__.
Anything less than 100% coverage will be frowned upon once the project is up and running.

Installation |PyPIversion|
--------------------------

This package is deployed to
`PyPi <https://badge.fury.io/py/pyiddidf>`__ and is available
via ``pip install pyiddidf``. The wheel is also posted to the
`Github Release
Page <https://github.com/Myoldmopar/py-idd-idf/releases/>`__ for
manual download/installation if desired.

.. |image0| image:: https://readthedocs.org/projects/python-iddidf-library-for-energyplus/badge/?version=latest
   :target: http://python-iddidf-library-for-energyplus.readthedocs.io/en/latest/?badge=latest
.. |image1| image:: https://travis-ci.org/Myoldmopar/py-idd-idf.svg?branch=master
   :target: https://travis-ci.org/Myoldmopar/py-idd-idf
.. |CoverageStatus| image:: https://coveralls.io/repos/github/Myoldmopar/py-idd-idf/badge.svg?branch=master
   :target: https://coveralls.io/github/Myoldmopar/py-idd-idf?branch=master
.. |PyPIversion| image:: https://badge.fury.io/py/pyiddidf.svg
   :target: https://badge.fury.io/py/pyiddidf
