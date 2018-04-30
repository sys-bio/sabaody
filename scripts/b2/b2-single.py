# B2 non-forking version

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-single")
sc = SparkContext(conf=conf)

from sabaody import Problem
from obj import B2Model
from params import getDefaultParamValues, getLowerBound, getUpperBound

#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

print('hi')

b2prob = Problem(B2Model,getLowerBound(),getUpperBound())

e = B2Model()
print('Initial score: {}'.format(e.evaluate(getDefaultParamValues())))