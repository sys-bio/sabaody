from pandas import read_csv, DataFrame

from os.path import join, dirname, realpath
from pprint import pprint
import arrow
from influxdb import InfluxDBClient
from ast import literal_eval
# from numpy import array
import json
from numpy import array
import matplotlib.pyplot as plt
from pprint import pprint

import argparse
parser = argparse.ArgumentParser(description='Run central migration service.')
parser.add_argument('tsv',
                    help='The input tsv.')
args = parser.parse_args()
tsv = args.tsv

if __name__ == '__main__':
    d = read_csv(tsv, sep='\t', header=0)

    replicates = d.groupby(('NumIslands','Description'))

    plots = {}
    for (n_islands, desc), group in replicates:
        desc = desc.replace('Bidirectional chain', 'Singleton')
        topology, algorithm = desc.split(', ')
        plots.setdefault(n_islands, {})
        # print(n_islands, desc, topology, algorithm)
        # print(group['MetricId'])
        for metricid in group['MetricId']:
            plots[n_islands][algorithm] = {}
            with open(join(realpath(dirname(__file__)), 'traces', metricid+'.json')) as f:
                plots[n_islands][algorithm].update({island_id: array(trace) for island_id, trace in json.load(f).items()})

    # pprint(plots)
    # print(plots.keys())
    # print(plots[1])

    nrows = 3
    ncols = 3
    colors = {1: 'C1', 16: 'C2'}
    for n_islands in [1, 16]:
        algorithms_list = sorted([algorithm for algorithm in plots[n_islands].keys()])
        for k,algorithm in enumerate(algorithms_list):
            # print(algorithm)
            # row = int(k/nrows)
            # col = k%ncols
            plt.subplot(nrows, ncols, k+1)
            plt.title(algorithm)
            for island_id, trace in plots[n_islands][algorithm].items():
                plt.semilogy(trace[:,0]/3600.,trace[:,1],color=colors[n_islands],linewidth=2)

    plt.savefig(join(realpath(dirname(__file__)), 'plot.pdf'), format='pdf')
