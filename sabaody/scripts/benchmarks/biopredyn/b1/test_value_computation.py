# test whether the SBML model produces the same results as the matlab model

from b1problem import B1Problem
from os.path import join, dirname, abspath, realpath

problem = B1Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b1-fixed.xml')))

problem.test_values()
