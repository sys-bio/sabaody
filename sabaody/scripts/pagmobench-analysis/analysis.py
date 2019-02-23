from pandas import read_csv, DataFrame

from os.path import join, dirname, realpath
from pprint import pprint

if __name__ == '__main__':
    d = read_csv(join(dirname(realpath(__file__)), 'pagmobench.tsv'), sep='\t', header=0)
    replicate_mean = DataFrame(d.groupby(('Benchmark','Description'))['ActualAvgRounds'].mean())
    # print(replicate_mean)
    rank = DataFrame(replicate_mean.groupby('Benchmark').rank())
    print(rank)
    # d['Rank'] = d.groupby(('Benchmark','Description'))['ActualAvgRounds'].rank()
    # d['MinRank'] = d.groupby('Description')['ActualAvgRounds'].min()
    # d['MaxRank'] = d.groupby('Description')['ActualAvgRounds'].max()
    # print(d)
    # print(d.groupby(('Benchmark','Description')))
    # pprint(d.groupby(('Benchmark','Description'))['ActualAvgRounds'].groups)
    # print(d.groupby(('Benchmark','Description'))['ActualAvgRounds'].rank())
