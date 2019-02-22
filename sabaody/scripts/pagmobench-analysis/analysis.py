from pandas import DataFrame

from os.path import join, dirname, realpath

if __name__ == '__main__':
    d = DataFrame.from_csv(join(dirname(realpath(__file__)), 'pagmobench.tsv'), sep='\t', header=0)
    print(d)
