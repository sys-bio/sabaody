from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("dumbeddown")
sc = SparkContext(conf=conf)

def spark_work(something):
        import pygmo as pg
        algorithm = pg.algorithm(pg.de())
        problem = pg.problem(pg.rosenbrock(5))
        a = pg.archipelago(n=2,algo=algorithm, prob=problem, pop_size=100)
        a.evolve(10)
        return 0

myresult = sc.parallelize(range(500),50).map(spark_work)
print(myresult.collect())