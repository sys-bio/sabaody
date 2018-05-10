from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("printout")
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
import logging
from pprint import PrettyPrinter
pp = PrettyPrinter(2)


print('hello')
try:
    nexecutors = int(sc._conf.get('spark.executor.instances'))
    print('Using {} executors'.format(nexecutors))
except:
    nexecutors = 4
    print('Cannot determine number of executors, using default value {}'.format(nexecutors))

print('\n')

def prox_method(x):
    from mod import spark_method
    return spark_method(x)

from time import time

start = time()

results = sc.range(nexecutors, numSlices=nexecutors).map(prox_method).collect()
print('Results:')
pp.pprint(results)
print('Result length: {}'.format(len(results)))
print('Duration: {:.2f} s'.format(time()-start))
#print('\nUnique results:')
#print(set(results))

#nums = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 20])
#print(nums.collect())

#sumAndCount = nums.map(lambda x: (x, 1)).fold((0, 0), (lambda x, y: (x[0] + y[0], x[1] + y[1])))

#print(sumAndCount)