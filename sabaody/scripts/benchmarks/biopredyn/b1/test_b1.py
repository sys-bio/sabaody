# test whether the SBML model produces the same results as the matlab model

from b1problem import B1Problem
from os.path import join, dirname, abspath, realpath
from numpy import allclose, isclose

def test_evaluate():
    problem = B1Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b1-copasi.xml')))
    from params import getDefaultParamValues
    assert isclose(problem.evaluate(getDefaultParamValues()), 1.0, rtol =1e-2)

def test_quantity_calculation():
    problem = B1Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b1-copasi.xml')))
    problem.reset()
    problem.r.reset()
    problem.r.resetAll()

    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())

    problem.r.simulate(0., 1., 10, problem.measured_quantity_ids)
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())

    problem.r.simulate(1., 10., 10, problem.measured_quantity_ids)
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())

    problem.r.simulate(10., 120., 100, problem.measured_quantity_ids)
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())
