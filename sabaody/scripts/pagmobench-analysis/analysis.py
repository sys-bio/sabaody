from pandas import read_csv

from os.path import join, dirname, realpath

if __name__ == '__main__':
    d = read_csv(join(dirname(realpath(__file__)), 'pagmobench.tsv'), sep='\t', header=0)
    print(d.groupby(('Benchmark','Description'))['ActualAvgRounds'].mean())
    # for benchmark,bench_data in d.groupby(('Benchmark','Description'))['ActualAvgRounds'].mean():
        # print(benchmark)
        # print(tuple(bench_data.keys()))
        # print(bench_data.groupby().groups)
