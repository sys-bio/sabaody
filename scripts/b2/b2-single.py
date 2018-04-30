from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-single")
sc = SparkContext(conf=conf)

from sabaody import Problem
from .obj import B2Model
from .params import lb, ub

b2prob = Problem(B2Model,lb,ub)