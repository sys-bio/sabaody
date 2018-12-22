# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

import argparse

parser = argparse.ArgumentParser(description='Get the name of a parameter.')
parser.add_argument('index', type=int,
                    help='The parameter index.')
args = parser.parse_args()

from params import param_index_to_name_map
print(param_index_to_name_map[args.index])
