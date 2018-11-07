# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

import argparse

parser = argparse.ArgumentParser(description='Generate a topology.')
parser.add_argument('--topology', required=True,
                    choices = ['ring', 'bidir-ring', 'one-way-ring'],
                    help='The topology to use')
parser.add_argument('output',
                    help='The output file.')

if topology_name == 'one-way-ring':
    return Archipelago(topology_factory.createOneWayRing(self.make_algorithm(),self.n_islands), metric)
elif topology_name == 'ring' or topology_name == 'bidir-ring':
    return Archipelago(topology_factory.createBidirRing(self.make_algorithm(),self.n_islands), metric)
else:
    raise RuntimeError('Unrecognized topology')