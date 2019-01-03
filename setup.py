#! /usr/bin/env python

from setuptools import setup

setup(name='sabaody',
      version='0.1.0',
      description='Distributed Island Model',
      author='Shaik Asifullah, J. Kyle Medley',
      packages=['sabaody'],
      install_requires=[
        'numpy>=1.14.2',
        'tellurium>=2.0.12',
        'networkx>=2.1',
        'pygmo>=2.7',
        'pyspark>=2.3.0',
        'cloudpickle>=0.5.2',
        'pymemcache>=1.4.4',
        'toolz>=0.9.0',
        'marshmallow>=2.15.2',
        'arrow>=0.12.1',
        'tornado>=5.0.2', # TODO: downgrade to 4.5.2
        'pytest-tornado>=0.5.0', # only for testing
        'APScheduler>=3.5.1',
        'requests>=2.18.0',
        'yarl>=1.2.4',
        'attrs>=18.1.0',
        'pytest-mock>=1.10.0',
        'kafka-python>=1.4.3',
        'interruptingcow>=0.8',
        'elasticsearch>=6.3.1',
        'influxdb>=5.2.0',
        'PyMySQL>=0.9.3',
        ],
      )
