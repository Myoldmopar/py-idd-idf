#!/usr/bin/env python

import codecs
import os
import setuptools

from pyiddidf import __version__


this_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as i_file:
    long_description = i_file.read()

setuptools.setup(
    name='energyplus_idd_idf_utilities',
    version=__version__,
    packages=['pyiddidf'],
    description='EnergyPlus idd/idf manipulation in Python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    license='UnlicensedForNow',
    install_requires=[],
    entry_points={
        'console_scripts': ['energyplus_idd_idf=pyiddidf.cli:main_cli']
    }
)
