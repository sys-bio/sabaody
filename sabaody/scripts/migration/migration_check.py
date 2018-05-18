# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from sabaody.migration_central import define_migrant_pool
from numpy import array
from uuid import uuid4

define_migrant_pool('http://luna:10100', uuid4(), 4)