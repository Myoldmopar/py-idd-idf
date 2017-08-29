#!/usr/bin/env python

import codecs
import os
import setuptools

from pyiddidf import __version__


this_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this_dir, 'README.rst'), encoding='utf-8') as i_file:
    long_description = i_file.read()

setuptools.setup(
    name='pyiddidf',
    version=__version__,
    description='EnergyPlus idd/idf manipulation in Python.',
    long_description=long_description,
    url='https://github.com/myoldmopar/py-idd-idf',
    author='Edwin Lee',
    author_email='leeed2001@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='cli energyplus',
    packages=setuptools.find_packages(exclude=['test', 'test.*', '.tox']),
    include_package_data=True,
    install_requires=[],
    extras_require={
        'test': ['coverage', 'unittest', 'coveralls'],
    },
    test_suite='nose.collector',
    tests_require=['nose'],
)
