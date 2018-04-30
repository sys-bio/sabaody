#! /usr/bin/env python

from setuptools import setup

setup(name='sabaody',
      version='0.1.0',
      description='Distributed Island Model',
      author='Shaik Asifullah, J. Kyle Medley',
      packages=['sabaody'],
      install_requires=[
        'tellurium',
        'networkx>=2.1',
        'pymemcache>=1.4.4',
        ],
      )
