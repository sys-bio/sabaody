# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

import requests, json

r = requests.get('http://luna:10100/version')
print(r.json())