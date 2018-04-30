# B2 non-forking version

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-single")
sc = SparkContext(conf=conf)

from sabaody import Problem
from .obj import B2Model
from .params import getLowerBound, getUpperBound

b2prob = Problem(B2Model,getLowerBound(),getUpperBound())