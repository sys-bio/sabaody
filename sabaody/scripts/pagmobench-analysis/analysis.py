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
    topology_rank_range = topology_rank_max-topology_rank_min
    # print(topology_rank_min['ActualAvgRounds'])
    print('Range per connectivity graph:')
    s = 0.
    for i in topology_rank_min.index:
        print(i, '{}-{}'.format(
            int(topology_rank_min['ActualAvgRounds'][i]), int(topology_rank_max['ActualAvgRounds'][i])),
            topology_rank_range['ActualAvgRounds'][i])
        s += float(topology_rank_range['ActualAvgRounds'][i])
    mean_range = float(topology_rank_range.mean())
    print('Average difference: {}'.format(mean_range))
    print(s/14.)
