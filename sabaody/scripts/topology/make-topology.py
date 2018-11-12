# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

import argparse
import pygmo as pg

parser = argparse.ArgumentParser(description='Generate a topology.')
parser.add_argument('--topology', required=True,
                    choices = ['ring', 'bidir-ring', 'one-way-ring'],
                    help='The topology to use')
parser.add_argument('--n-islands', required=True, type=int, default=10,
                    help='The number of islands to use in the topology')
parser.add_argument('--algorithm', required=True,
                    help='Algorithm to use in the optimization')
parser.add_argument('output',
                    help='The output file.')
args = parser.parse_args()

algorithm = getattr(pg,args.algorithm)
n_islands = args.n_islands

def generate_topology():
    if args.topology == 'one-way-ring':
        return Archipelago(topology_factory.createOneWayRing(algorithm,n_islands))
    elif args.topology == 'ring' or args.topology == 'bidir-ring':
        return Archipelago(topology_factory.createBidirRing(algorithm,n_islands))
    else:
        raise RuntimeError('Unrecognized topology')

from pickle import dump
with open(args.output, 'wb') as f:
    dump(generate_topology(), f)