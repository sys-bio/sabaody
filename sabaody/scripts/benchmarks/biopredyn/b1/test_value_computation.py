# test whether the SBML model produces the same results as the matlab model

from b1problem import B1Problem
from os.path import join, dirname, abspath, realpath
from numpy import allclose

def test_values():
    problem = B1Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b1-copasi.xml')))
    problem.reset()
    problem.r.reset()
    problem.r.resetAll()

    # print(problem.getCurrentValues_matlab() - problem.getCurrentValues())
    # print('rr: cell*Vmax_1166*(s_0565 - s_0563)/Km0565_1166/(1 + s_0565/Km0565_1166 + 1 + s_0563/Km0563_1166 - 1) = ')
    # print('  {cell}*{Vmax_1166:.2f}*({s_0565:.2f} - {s_0563:.2f})/{Km0565_1166}/(1 + {s_0565:.2f}/{Km0565_1166} + 1 + {s_0563:.2f}/{Km0563_1166} - 1) = '.format(
    #     cell=problem.r.cell,
    #     Vmax_1166=problem.r.Vmax_1166,
    #     s_0565=problem.r.s_0565,
    #     s_0563=problem.r.s_0563,
    #     Km0565_1166=problem.r.Km0565_1166,
    #     Km0563_1166=problem.r.Km0563_1166,
    # ))
    # print(' ', problem.r.r_1166)

    # print('ml: problem.getParameterValue(1613-1) * (problem.r.s_0565 - problem.r.s_0563) / problem.getParameterValue(1614-1) / (1 + problem.r.s_0565 / problem.getParameterValue(1614-1) + 1 + problem.r.s_0563 / problem.getParameterValue(1615-1) - 1) = ')
    # print('ml: {p1613} * ({s_0565} - {s_0563}) / {p1614} / (1 + {s_0565} / {p1614} + 1 + {s_0563} / {p1615} - 1) = '.format(
    #     p1613=problem.getParameterValue(1613-1),
    #     s_0565=problem.r.s_0565,
    #     s_0563=problem.r.s_0563,
    #     p1614=problem.getParameterValue(1614-1),
    #     p1615=problem.getParameterValue(1615-1),
    # ))
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())
    # print(problem.getCurrentValues())

    problem.r.simulate(0., 1., 10, problem.measured_quantity_ids)
    # print(problem.getCurrentValues_matlab() - problem.getCurrentValues())
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())

    problem.r.simulate(1., 10., 10, problem.measured_quantity_ids)
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())

    problem.r.simulate(10., 120., 100, problem.measured_quantity_ids)
    assert allclose(problem.getCurrentValues_matlab(), problem.getCurrentValues())
