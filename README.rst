EnergyPlus Python Transition
============================

Python version of the E+ input file transition utility

Documentation |image0|
----------------------

Documentation (just skeleton for now) is hosted on
`ReadTheDocs <http://energyplus-python-transition.readthedocs.org/en/latest/>`__.
Documentation includes installation and usage tips, as well as a full documentation of the code base. To build the
documentation, enter the docs/ subdirectory and execute ``make html``; then open
``/docs/_build/html/index.html`` to see the documentation.

Testing |image1|
----------------

The source is tested using the python unittest framework. To execute all
the unit tests, just execute the test file (since it calls
``unittest.main()``): ``python test/test_main.py``. The tests are also
executed by `Travis
CI <https://travis-ci.org/Myoldmopar/ep-transition>`__.

Test Coverage |Coverage Status|
-------------------------------

Coverage of the code from unit testing is reported by
`Travis <https://travis-ci.org/Myoldmopar/ep-transition>`__ to
`Coveralls <https://coveralls.io/github/Myoldmopar/ep-transition>`__.
Anything less than 100% coverage will be frowned upon.

Installation |PyPI version|
---------------------------

This package is deployed to
`PyPi <https://pypi.python.org/pypi/eptransition/>`__ and is available
via ``pip install eptransition``. The wheel is also posted to the
`Github Release
Page <https://github.com/Myoldmopar/ep-transition/releases/>`__ for
manual download/installation if desired.

.. |image0| image:: https://readthedocs.org/projects/energyplus-python-transition/badge/?version=latest
   :target: http://energyplus-python-transition.readthedocs.org/en/latest/
.. |image1| image:: https://travis-ci.org/Myoldmopar/ep-transition.svg?branch=master
   :target: https://travis-ci.org/Myoldmopar/ep-transition
.. |Coverage Status| image:: https://coveralls.io/repos/github/Myoldmopar/ep-transition/badge.svg?branch=master
   :target: https://coveralls.io/github/Myoldmopar/ep-transition?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/eptransition.svg
   :target: https://badge.fury.io/py/eptransition
