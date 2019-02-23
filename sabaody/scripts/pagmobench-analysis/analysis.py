from pandas import read_csv, DataFrame

from os.path import join, dirname, realpath
from pprint import pprint

if __name__ == '__main__':
    d = read_csv(join(dirname(realpath(__file__)), 'pagmobench.tsv'), sep='\t', header=0)
    d['Topology'] = tuple(desc.split(', ')[0] for desc in d['Description'])
    # print(d)
    topology_mean = DataFrame(d.groupby(('Benchmark','Topology'))['ActualAvgRounds'].mean())
    # print(topology_mean)
    topology_rank = DataFrame(topology_mean.groupby('Benchmark').rank())
    # print(topology_rank)
    topology_rank_min = topology_rank.min(axis=0,level=1)
    topology_rank_max = topology_rank.max(axis=0,level=1)
    # print(topology_rank_min['ActualAvgRounds'])
    for i in topology_rank_min.index:
        print(i, topology_rank_min['ActualAvgRounds'][i])
    for topology in topology_rank_min['ActualAvgRounds']:
        print(topology)
