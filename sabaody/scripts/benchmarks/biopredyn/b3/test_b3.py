from b3problem import B3Problem
from os.path import join, dirname, abspath, realpath
from numpy import allclose, isclose

problem = B3Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b3.xml')))
