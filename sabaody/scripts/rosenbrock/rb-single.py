# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("rb-driver")
sc = SparkContext(conf=conf)
import pygmo as pg

from sabaody import Archipelago

from rbsetup import RBRun

from numpy import array, save, savez, mean, std, nan_to_num, vstack

from tempfile import gettempdir
from os.path import join
import json

single_champions = []
N = 1
for i in range(N):
    with RBRun('luna', 11211) as run:
        print('Started run {} of {}'.format(i+1,N))
        from rbsetup import make_problem
        algorithm = pg.de(gen=10)
        problem = make_problem()
        i = pg.island(algo=algorithm, prob=problem, size=20)

        rounds = 10
        c = []
        for x in range(rounds):
            i.evolve()
            i.wait()
            c.append(float(i.get_population().champion_f[0]))
            print('round {}'.format(x))
            print(i.get_population().champion_f)
            print(i.get_population().get_x()[0,:])
        single_champions.append(array(c))

single_champions_stack = vstack(single_champions)
single_champions_mean = mean(single_champions_stack, axis=0)
single_champions_std = std(single_champions_stack, axis=0)
savez('/tmp/rb-single-champions.npz', single_champions_mean=single_champions_mean, single_champions_std=single_champions_std)