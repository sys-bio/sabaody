"""
differential_evolution: The differential evolution global optimization algorithm
Added by Andrew Nelson 2014
"""
from __future__ import division, print_function, absolute_import
import numpy as np, time, random
from Topology import Topology
from obj import B4Model
from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("GEN-DIFF-EVOL").setMaster("local[4]")
sc = SparkContext(conf=conf)

def beale_function(x):
    b4 = B4Model()
    b4.r.cpep = x[0]
    b4.r.cg6p = x[1]
    b4.r.cpyr = x[2]
    b4.r.cf6p = x[3]
    b4.r.cglcex = x[4]
    b4.r.cg1p = x[5]
    b4.r.cpg = x[6]
    b4.r.cfdp = x[7]
    mse = b4.calcObjective()
    return mse


number_of_islands = 4
KEY = "B2Test"
def island_method(island_params):
    island_marker = island_params[0]
    seed = island_params[1]
    cost_func = beale_function


    cpep = (1,10)
    cg6p = (1,10)
    cpyr = (1,10)
    cf6p = (1,10)
    cglcex = (1,10)
    cg1p = (0,1)
    
    cpg = (0,1)
    cfdp = (0,1)
    


    bounds = [cpep,cg6p,cpyr,cf6p,cglcex,cg1p,cpg,cfdp]
    popsize = 20
    mutatation_factor = 0.5
    recombination = 0.7
    maxiter = 20
    num_migrations = 4
    result = differential_evolution(cost_func,bounds, island_marker=island_marker,seed=seed,key=KEY,maxiter=maxiter)
    #client.set(marker,str(result))
    return (island_marker,str(result))

parallelization = []
random_seeds = random.sample(range(1, 100), number_of_islands)
for i in range(1,number_of_islands+1):
    parallelization.append((KEY+str(i),random_seeds[i-1]))



island_rdd = sc.parallelize(parallelization)
island_rdd = island_rdd.map(island_method)
print(island_rdd.collect())