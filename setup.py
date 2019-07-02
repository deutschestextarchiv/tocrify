# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
from pkg_resources import resource_filename, Requirement

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tocrify',
    version='0.0.1',
    description='Pimp OCR with structural information from METS',
    long_description=readme,
    author='Kay-Michael Würzner, Matthias Boenig',
    author_email='wuerzner@bbaw.de, boenig@bbaw.de',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'tocrify' : ['data/mets2hocr.yml']},
    install_requires=[
    ],
    entry_points={
          'console_scripts': [
              'tocrify=tocrify.scripts.tocrify:cli',
          ]
    },
)
