#!/usr/bin/env python

import codecs
import os
import setuptools

from energyplus_iddidf import __version__


this_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as i_file:
    long_description = i_file.read()

setuptools.setup(
    name='energyplus_idd_idf_utilities',
    version=__version__,
    packages=['energyplus_iddidf'],
    description='EnergyPlus idd/idf manipulation in Python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/myoldmopar/py-idd-idf',
    author='Edwin Lee, for NREL, for the United States Department of Energy',
    license='ModifiedBSD',
    install_requires=[],
    entry_points={
        'console_scripts': ['energyplus_idd_idf=energyplus_iddidf.cli:main_cli']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Utilities',
    ],
    platforms=[
        'Linux (Tested on Ubuntu)', 'MacOSX', 'Windows'
    ],
    keywords=[
        'energyplus_launch', 'ep_launch',
        'EnergyPlus', 'eplus', 'Energy+',
        'Building Simulation', 'Whole Building Energy Simulation',
        'Heat Transfer', 'HVAC', 'Modeling',
    ]
)
