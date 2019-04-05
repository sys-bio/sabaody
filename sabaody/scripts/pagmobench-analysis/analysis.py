from pandas import read_csv, DataFrame

from os.path import join, dirname, realpath
from pprint import pprint

if __name__ == '__main__':
    d = read_csv(join(dirname(realpath(__file__)), 'pagmobench.tsv'), sep='\t', header=0)
    d['Topology'] = tuple(desc.split(', ')[0] for desc in d['Description'])
    d['Algorithm'] = tuple(desc.split(', ')[1] for desc in d['Description'])

    topology_mean = DataFrame(d.groupby(('Benchmark','Topology'))['ActualAvgRounds'].mean())
    topology_rank = DataFrame(topology_mean.groupby('Benchmark').rank())
    topology_rank_min = topology_rank.min(axis=0,level=1)
    topology_rank_max = topology_rank.max(axis=0,level=1)
    topology_rank_range = topology_rank_max-topology_rank_min
    topology_rank_median = 0.5*(topology_rank_min + topology_rank_max)

    print('Range (topology):')
    for i in topology_rank_median.sort_values(by='ActualAvgRounds').index:
        print('  ', i, '{}-{}'.format(
            int(topology_rank_min['ActualAvgRounds'][i]), int(topology_rank_max['ActualAvgRounds'][i])))
    topology_mean_range = float(topology_rank_range.mean())
    print('Average range: {}'.format(topology_mean_range))
    print('\n\n\n')

    algorithm_mean = DataFrame(d.groupby(('Benchmark','Algorithm'))['ActualAvgRounds'].mean())
    algorithm_rank = DataFrame(algorithm_mean.groupby('Benchmark').rank())
    algorithm_rank_min = algorithm_rank.min(axis=0,level=1)
    algorithm_rank_max = algorithm_rank.max(axis=0,level=1)
    algorithm_rank_range = algorithm_rank_max-algorithm_rank_min
    algorithm_rank_median = 0.5*(algorithm_rank_min + algorithm_rank_max)

    print('Range (algorithm):')
    for i in algorithm_rank_median.sort_values(by='ActualAvgRounds').index:
        print('  ', i, '{}-{}'.format(
            int(algorithm_rank_min['ActualAvgRounds'][i]), int(algorithm_rank_max['ActualAvgRounds'][i])))
    algorithm_mean_range = float(algorithm_rank_range.mean())
    print('Average range: {}'.format(algorithm_mean_range))

    # print latex table
    print('\nLatex:\n')
    for i,j in zip(topology_rank_median.sort_values(by='ActualAvgRounds').index, algorithm_rank_median.sort_values(by='ActualAvgRounds').index):
        print(i.replace('-','--'), '&', '{}--{}'.format(
            int(topology_rank_min['ActualAvgRounds'][i]), int(topology_rank_max['ActualAvgRounds'][i])),
            '&', j.replace('_',' '), '&', '{}--{}'.format(
            int(algorithm_rank_min['ActualAvgRounds'][j]), int(algorithm_rank_max['ActualAvgRounds'][j])),
            r'\\')
    print('Avg. diff.', '&', '{:.2f}'.format(topology_mean_range), '&', 'Avg. diff.', '&', '{:.2f}'.format(algorithm_mean_range))
